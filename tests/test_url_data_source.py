"""
Tests for URL data source functionality.

This module tests the URLDataSource class which provides:
- HTTP/HTTPS URL data fetching
- Basic Auth and Bearer token authentication
- JSON and CSV parsing with schema inference
- Retry logic on server errors
- Response size limits
"""

import pytest
from pydantic import ValidationError


class TestURLDataSourceConfig:
    """Tests for URLDataSource configuration models."""

    def test_config_validates_http_url(self):
        """
        Test that URLDataSourceConfig accepts HTTP URLs.

        Expected behavior:
        - HTTP URLs should be accepted
        - HTTPS URLs should be accepted
        - Other schemes should be rejected
        """
        from scripts.url_data_source import URLDataSourceConfig

        # HTTP should work
        config_http = URLDataSourceConfig(
            url="http://example.com/data.json",
            format="json",
            table_name="test_table"
        )
        assert config_http.url == "http://example.com/data.json"

        # HTTPS should work
        config_https = URLDataSourceConfig(
            url="https://example.com/data.csv",
            format="csv",
            table_name="test_table"
        )
        assert config_https.url == "https://example.com/data.csv"

    def test_config_rejects_non_http_schemes(self):
        """
        Test that URLDataSourceConfig rejects non-HTTP schemes.

        Expected behavior:
        - ftp:// should raise ValidationError
        - file:// should raise ValidationError
        - javascript: should raise ValidationError
        """
        from scripts.url_data_source import URLDataSourceConfig

        with pytest.raises(ValidationError, match="http://|https://"):
            URLDataSourceConfig(
                url="ftp://example.com/data.json",
                format="json",
                table_name="test_table"
            )

        with pytest.raises(ValidationError, match="http://|https://"):
            URLDataSourceConfig(
                url="file:///path/to/data.json",
                format="json",
                table_name="test_table"
            )

    def test_config_accepts_json_or_csv_format(self):
        """
        Test that URLDataSourceConfig accepts only 'json' or 'csv' format.

        Expected behavior:
        - 'json' format should be accepted
        - 'csv' format should be accepted
        - Other values should raise ValidationError
        """
        from scripts.url_data_source import URLDataSourceConfig

        # json should work
        config_json = URLDataSourceConfig(
            url="https://example.com/data",
            format="json",
            table_name="test_table"
        )
        assert config_json.format == "json"

        # csv should work
        config_csv = URLDataSourceConfig(
            url="https://example.com/data",
            format="csv",
            table_name="test_table"
        )
        assert config_csv.format == "csv"

        # Other formats should fail
        with pytest.raises(ValidationError):
            URLDataSourceConfig(
                url="https://example.com/data",
                format="xml",
                table_name="test_table"
            )

    def test_config_accepts_basic_auth(self):
        """
        Test that URLDataSourceConfig accepts BasicAuthConfig.

        Expected behavior:
        - BasicAuthConfig with username/password should be accepted
        - type field should default to 'basic'
        """
        from scripts.url_data_source import (
            URLDataSourceConfig,
            BasicAuthConfig
        )

        auth = BasicAuthConfig(username="user", password="secret")
        config = URLDataSourceConfig(
            url="https://example.com/data",
            format="json",
            table_name="test_table",
            auth=auth
        )

        assert config.auth is not None
        assert config.auth.username == "user"
        assert config.auth.type == "basic"

    def test_config_accepts_bearer_auth(self):
        """
        Test that URLDataSourceConfig accepts BearerAuthConfig.

        Expected behavior:
        - BearerAuthConfig with token should be accepted
        - type field should default to 'bearer'
        """
        from scripts.url_data_source import (
            URLDataSourceConfig,
            BearerAuthConfig
        )

        auth = BearerAuthConfig(token="my-secret-token")
        config = URLDataSourceConfig(
            url="https://example.com/data",
            format="json",
            table_name="test_table",
            auth=auth
        )

        assert config.auth is not None
        assert config.auth.type == "bearer"

    def test_secret_str_prevents_token_exposure(self):
        """
        Test that SecretStr prevents token/password from appearing in str representation.

        Expected behavior:
        - Password should not appear in string representation
        - Token should not appear in string representation
        - SecretStr.get_secret_value() should return actual value
        """
        from scripts.url_data_source import (
            BasicAuthConfig,
            BearerAuthConfig
        )

        # Test BasicAuth password hiding
        basic_auth = BasicAuthConfig(username="user", password="my-secret-password")
        assert "my-secret-password" not in str(basic_auth)
        assert basic_auth.password.get_secret_value() == "my-secret-password"

        # Test BearerAuth token hiding
        bearer_auth = BearerAuthConfig(token="my-secret-token")
        assert "my-secret-token" not in str(bearer_auth)
        assert bearer_auth.token.get_secret_value() == "my-secret-token"

    def test_config_timeout_validation(self):
        """
        Test that timeout is validated within acceptable range.

        Expected behavior:
        - Default timeout should be 30.0 seconds
        - Timeout should be >= 1.0 seconds
        - Timeout should be <= 300.0 seconds (5 minutes)
        """
        from scripts.url_data_source import URLDataSourceConfig

        # Default timeout
        config = URLDataSourceConfig(
            url="https://example.com/data",
            format="json",
            table_name="test_table"
        )
        assert config.timeout == 30.0

        # Valid range
        config_min = URLDataSourceConfig(
            url="https://example.com/data",
            format="json",
            table_name="test_table",
            timeout=1.0
        )
        assert config_min.timeout == 1.0

        config_max = URLDataSourceConfig(
            url="https://example.com/data",
            format="json",
            table_name="test_table",
            timeout=300.0
        )
        assert config_max.timeout == 300.0

        # Below minimum
        with pytest.raises(ValidationError):
            URLDataSourceConfig(
                url="https://example.com/data",
                format="json",
                table_name="test_table",
                timeout=0.5
            )

        # Above maximum
        with pytest.raises(ValidationError):
            URLDataSourceConfig(
                url="https://example.com/data",
                format="json",
                table_name="test_table",
                timeout=400.0
            )


class TestURLDataSourceFetch:
    """Tests for URLDataSource async fetch functionality."""

    @pytest.mark.asyncio
    async def test_fetch_json_without_authentication(self):
        """
        Test fetching JSON from URL without authentication.

        Expected behavior:
        - Fetch JSON data successfully
        - Parse JSON response into list of dicts
        """
        import httpx
        import respx

        from scripts.url_data_source import URLDataSource, URLDataSourceConfig

        config = URLDataSourceConfig(
            url="https://api.example.com/data",
            format="json",
            table_name="test_table"
        )

        with respx.mock:
            respx.get("https://api.example.com/data").mock(
                return_value=httpx.Response(200, json={"data": [{"id": 1, "name": "test"}]})
            )

            source = URLDataSource(config)
            records = await source.fetch_and_parse()

        assert len(records) == 1
        assert records[0]["id"] == 1
        assert records[0]["name"] == "test"

    @pytest.mark.asyncio
    async def test_fetch_with_basic_auth(self):
        """
        Test fetching with Basic Auth includes correct Authorization header.

        Expected behavior:
        - Basic Auth credentials should be sent in Authorization header
        - Base64-encoded credentials should be present
        """
        import httpx
        import respx
        import base64

        from scripts.url_data_source import (
            URLDataSource,
            URLDataSourceConfig,
            BasicAuthConfig
        )

        config = URLDataSourceConfig(
            url="https://api.example.com/protected",
            format="json",
            table_name="test_table",
            auth=BasicAuthConfig(username="testuser", password="testpass")
        )

        auth_header_captured = None

        def capture_auth(request):
            nonlocal auth_header_captured
            auth_header_captured = request.headers.get("Authorization")
            return httpx.Response(200, json=[{"id": 1}])

        with respx.mock as mock:
            mock.get("https://api.example.com/protected").mock(side_effect=capture_auth)

            source = URLDataSource(config)
            await source.fetch_and_parse()

        # Verify Basic Auth header is present
        assert auth_header_captured is not None
        assert auth_header_captured.startswith("Basic ")

        # Verify credentials are correct
        encoded = auth_header_captured.replace("Basic ", "")
        decoded = base64.b64decode(encoded).decode()
        assert decoded == "testuser:testpass"

    @pytest.mark.asyncio
    async def test_fetch_with_bearer_auth(self):
        """
        Test fetching with Bearer token includes correct Authorization header.

        Expected behavior:
        - Bearer token should be sent in Authorization header
        - Header format: 'Bearer {token}'
        """
        import httpx
        import respx

        from scripts.url_data_source import (
            URLDataSource,
            URLDataSourceConfig,
            BearerAuthConfig
        )

        config = URLDataSourceConfig(
            url="https://api.example.com/protected",
            format="json",
            table_name="test_table",
            auth=BearerAuthConfig(token="secret-token-123")
        )

        auth_header_captured = None

        def capture_auth(request):
            nonlocal auth_header_captured
            auth_header_captured = request.headers.get("Authorization")
            return httpx.Response(200, json=[{"id": 1}])

        with respx.mock as mock:
            mock.get("https://api.example.com/protected").mock(side_effect=capture_auth)

            source = URLDataSource(config)
            await source.fetch_and_parse()

        # Verify Bearer token header is correct
        assert auth_header_captured == "Bearer secret-token-123"

    @pytest.mark.asyncio
    async def test_retry_on_5xx_server_errors(self):
        """
        Test retry on 5xx server errors (max 3 attempts).

        Expected behavior:
        - 500 errors should trigger retry
        - After 3 failures, should raise the error
        - Successful response after retry should work
        """
        import httpx
        import respx

        from scripts.url_data_source import URLDataSource, URLDataSourceConfig

        config = URLDataSourceConfig(
            url="https://api.example.com/flaky",
            format="json",
            table_name="test_table"
        )

        with respx.mock as mock:
            # First call returns 500, second returns success
            route = mock.get("https://api.example.com/flaky").mock(
                side_effect=[
                    httpx.Response(500, json={"error": "Internal error"}),
                    httpx.Response(200, json=[{"id": 1}])
                ]
            )

            source = URLDataSource(config)
            records = await source.fetch_and_parse()

        # Verify retry happened (2 calls made)
        assert route.call_count == 2
        assert len(records) == 1

    @pytest.mark.asyncio
    async def test_response_size_limit_enforced(self):
        """
        Test that response size limit (100MB) is enforced.

        Expected behavior:
        - Responses larger than 100MB should be rejected
        - Content-Length header should be checked before loading body
        """
        import httpx
        import respx

        from scripts.url_data_source import URLDataSource, URLDataSourceConfig

        config = URLDataSourceConfig(
            url="https://api.example.com/large",
            format="json",
            table_name="test_table"
        )

        with respx.mock:
            respx.get("https://api.example.com/large").mock(
                return_value=httpx.Response(
                    200,
                    headers={"content-length": "150000000"},  # 150MB
                    json={}
                )
            )

            source = URLDataSource(config)

            with pytest.raises(ValueError, match="too large"):
                await source.fetch()

    @pytest.mark.asyncio
    async def test_http_4xx_errors_no_retry(self):
        """
        Test that HTTP 4xx errors are raised without retry.

        Expected behavior:
        - 401 Unauthorized should not trigger retry
        - 404 Not Found should not trigger retry
        - Error should be raised immediately
        """
        import httpx
        import respx

        from scripts.url_data_source import URLDataSource, URLDataSourceConfig

        config = URLDataSourceConfig(
            url="https://api.example.com/notfound",
            format="json",
            table_name="test_table"
        )

        with respx.mock as mock:
            # 404 should not trigger retry
            route = mock.get("https://api.example.com/notfound").mock(
                return_value=httpx.Response(404, json={"error": "Not found"})
            )

            source = URLDataSource(config)

            with pytest.raises(httpx.HTTPStatusError):
                await source.fetch()

        # Should only be called once (no retry)
        assert route.call_count == 1

    @pytest.mark.asyncio
    async def test_timeout_on_slow_response(self):
        """
        Test that timeout exception is raised on slow responses.

        Expected behavior:
        - Requests exceeding timeout should raise TimeoutException
        - Timeout should be configurable via config
        """
        import httpx
        import respx

        from scripts.url_data_source import URLDataSource, URLDataSourceConfig

        config = URLDataSourceConfig(
            url="https://api.example.com/slow",
            format="json",
            table_name="test_table",
            timeout=1.0  # Minimum valid timeout
        )

        with respx.mock as mock:
            # Simulate slow response by raising timeout exception
            route = mock.get("https://api.example.com/slow").mock(
                side_effect=httpx.TimeoutException("Request timed out")
            )

            source = URLDataSource(config)

            with pytest.raises(httpx.TimeoutException):
                await source.fetch()
