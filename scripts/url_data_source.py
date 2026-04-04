"""
URL Data Source Module.

Provides async HTTP data fetching with authentication support:
- URLDataSourceConfig: Pydantic configuration model
- BasicAuthConfig: Basic authentication configuration
- BearerAuthConfig: Bearer token authentication configuration
- URLDataSource: Async HTTP client with retry and parsing

Usage:
    from scripts.url_data_source import URLDataSource, URLDataSourceConfig

    config = URLDataSourceConfig(
        url="https://api.example.com/data",
        format="json",
        table_name="api_data"
    )

    source = URLDataSource(config)
    records = await source.fetch_and_parse()
"""

from typing import Literal, Optional, Union

from pydantic import BaseModel, Field, SecretStr, field_validator
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import structlog

logger = structlog.get_logger(__name__)

# Constants
MAX_RETRIES = 3
MAX_RESPONSE_SIZE = 100 * 1024 * 1024  # 100MB


class ServerError(Exception):
    """Exception for 5xx server errors that should trigger retry."""
    pass


class BasicAuthConfig(BaseModel):
    """Basic authentication configuration.

    Attributes:
        type: Authentication type, always 'basic'
        username: Username for Basic Auth
        password: Password for Basic Auth (stored as SecretStr)
    """
    type: Literal["basic"] = "basic"
    username: str = Field(description="Username for Basic Auth")
    password: SecretStr = Field(description="Password for Basic Auth")


class BearerAuthConfig(BaseModel):
    """Bearer token authentication configuration.

    Attributes:
        type: Authentication type, always 'bearer'
        token: Bearer token value (stored as SecretStr)
    """
    type: Literal["bearer"] = "bearer"
    token: SecretStr = Field(description="Bearer token value")


# Union type for authentication configurations
AuthConfig = Union[BasicAuthConfig, BearerAuthConfig]


class URLDataSourceConfig(BaseModel):
    """Configuration for URL data source import.

    Attributes:
        url: HTTP/HTTPS URL to fetch data from
        format: Data format, either 'json' or 'csv'
        table_name: Target table name for the imported data
        auth: Optional authentication configuration
        timeout: Request timeout in seconds (1.0 - 300.0)
    """
    url: str = Field(description="HTTP/HTTPS URL to fetch data from")
    format: Literal["json", "csv"] = Field(description="Data format")
    table_name: str = Field(description="Target table name")
    auth: Optional[AuthConfig] = Field(default=None, description="Authentication config")
    timeout: float = Field(
        default=30.0,
        ge=1.0,
        le=300.0,
        description="Request timeout in seconds"
    )

    @field_validator('url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate that URL uses HTTP or HTTPS scheme.

        Args:
            v: URL string to validate

        Returns:
            Validated URL string

        Raises:
            ValueError: If URL does not start with http:// or https://
        """
        if not v.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
        return v


class URLDataSource:
    """Async HTTP data source fetcher with authentication support.

    Provides:
    - Async HTTP fetching with retry logic
    - Basic Auth and Bearer token authentication
    - Response size validation
    - JSON and CSV parsing

    Attributes:
        config: URLDataSource configuration
    """

    def __init__(self, config: URLDataSourceConfig):
        """Initialize the URL data source.

        Args:
            config: Configuration for the URL data source
        """
        self.config = config

    def _build_auth(self) -> Optional[httpx.Auth]:
        """Build httpx auth from configuration.

        Returns:
            httpx.Auth for Basic Auth, None otherwise (Bearer handled via headers)
        """
        if self.config.auth is None:
            return None

        if isinstance(self.config.auth, BasicAuthConfig):
            return httpx.BasicAuth(
                self.config.auth.username,
                self.config.auth.password.get_secret_value()
            )

        # Bearer token is handled via headers
        return None

    def _build_headers(self) -> dict[str, str]:
        """Build request headers including auth headers.

        Returns:
            Dictionary of HTTP headers
        """
        headers = {
            "Accept": "application/json, text/csv, text/plain",
            "User-Agent": "echart-skill/1.0"
        }

        if isinstance(self.config.auth, BearerAuthConfig):
            headers["Authorization"] = f"Bearer {self.config.auth.token.get_secret_value()}"

        return headers

    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        retry=retry_if_exception_type(ServerError),
        reraise=True
    )
    async def fetch(self) -> str:
        """Fetch data from URL with retry logic.

        Retries only on 5xx server errors. 4xx client errors are not retried.

        Returns:
            Raw response content as string

        Raises:
            httpx.HTTPStatusError: On 4xx HTTP errors (no retry)
            ServerError: On 5xx HTTP errors (triggers retry)
            httpx.TimeoutException: On timeout
            ValueError: If response too large
        """
        timeout = httpx.Timeout(self.config.timeout)

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(
                self.config.url,
                auth=self._build_auth(),
                headers=self._build_headers()
            )

            # Handle 5xx errors separately for retry
            if response.status_code >= 500:
                raise ServerError(
                    f"Server error {response.status_code}: {response.text[:200]}"
                )

            # Raise on 4xx errors (no retry)
            response.raise_for_status()

            # Check content length
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > MAX_RESPONSE_SIZE:
                raise ValueError(
                    f"Response too large: {int(content_length) / 1024 / 1024:.1f}MB > 100MB limit"
                )

            return response.text

    async def fetch_and_parse(self) -> list[dict]:
        """Fetch and parse data from URL.

        Returns:
            List of dictionaries representing rows
        """
        content = await self.fetch()

        if self.config.format == "json":
            return self._parse_json(content)
        else:
            return self._parse_csv(content)

    def _parse_json(self, content: str) -> list[dict]:
        """Parse JSON content and flatten nested structures.

        Args:
            content: Raw JSON string

        Returns:
            List of dictionaries

        Raises:
            ValueError: If JSON is invalid or not an array
        """
        import json
        import pandas as pd
        import sys
        import os

        # Add project root to path for imports
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from scripts.data_importer import clean_column_names

        data = json.loads(content)

        # Auto-detect array location
        if isinstance(data, dict):
            # Check common wrapper keys
            for key in ['data', 'results', 'items', 'records', 'rows']:
                if key in data and isinstance(data[key], list):
                    data = data[key]
                    break
            else:
                # Single object, wrap in list
                data = [data]

        if not isinstance(data, list):
            raise ValueError(f"Expected JSON array, got {type(data).__name__}")

        if not data:
            return []

        # Flatten nested objects using pandas
        df = pd.json_normalize(data, sep='_')

        # Clean column names
        df.columns = clean_column_names(df.columns.tolist())

        return df.to_dict(orient='records')

    def _parse_csv(self, content: str) -> list[dict]:
        """Parse CSV content into list of dicts.

        Args:
            content: Raw CSV string

        Returns:
            List of dictionaries
        """
        import io
        import pandas as pd
        import sys
        import os

        # Add project root to path for imports
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from scripts.data_importer import clean_column_names

        df = pd.read_csv(io.StringIO(content))

        # Clean column names
        df.columns = clean_column_names(df.columns.tolist())

        return df.to_dict(orient='records')


def infer_schema_from_json(data: Union[list[dict], dict]) -> dict[str, str]:
    """Infer column types from JSON data.

    Handles nested structures by flattening with underscore notation.
    Returns a mapping of column names to SQLite types.

    Args:
        data: JSON data (list of dicts or single dict)

    Returns:
        Dict mapping column names to SQLite types (INTEGER, REAL, TEXT)
    """
    import pandas as pd

    # Handle single object response
    if isinstance(data, dict):
        # Check if it's a wrapper with data array
        for key in ['data', 'results', 'items', 'records']:
            if key in data and isinstance(data[key], list):
                data = data[key]
                break
        else:
            data = [data]  # Single record

    if not data:
        return {}

    # Flatten nested structures
    df = pd.json_normalize(data, sep='_')

    # Infer types - map pandas dtypes to SQLite types
    type_map = {
        'int64': 'INTEGER',
        'Int64': 'INTEGER',
        'float64': 'REAL',
        'Float64': 'REAL',
        'bool': 'INTEGER',
        'boolean': 'INTEGER',
        'object': 'TEXT',
        'datetime64[ns]': 'TEXT',  # Store as ISO string
    }

    schema = {}
    for col in df.columns:
        pandas_type = str(df[col].dtype)
        schema[col] = type_map.get(pandas_type, 'TEXT')

    return schema
