"""
Database Configuration Module.

Provides configuration loading and validation for external database connections.
Supports MySQL, PostgreSQL, SQLite, and MongoDB with secure credential handling.

Usage:
    from scripts.db_config import load_config, resolve_env_vars
    
    config = load_config()  # Auto-discovers db_connections.json
    profile = config.connections["my_mysql"]
"""

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field, SecretStr, field_validator

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logging_config import get_logger

logger = get_logger(__name__)


class ConnectionProfile(BaseModel):
    """Single database connection configuration.
    
    Supports two modes:
    1. Full connection_string: "mysql://user:pass@host:port/db"
    2. Individual fields: host, port, database, username, password
    """
    type: Literal["mysql", "postgresql", "sqlite", "mongodb"] = Field(
        description="Database type"
    )
    
    # Either connection_string OR individual fields
    connection_string: Optional[str] = Field(
        default=None,
        description="Full connection string (alternative to individual fields)"
    )
    
    # Individual connection fields
    host: Optional[str] = Field(default=None, description="Database host")
    port: Optional[int] = Field(default=None, description="Database port")
    database: Optional[str] = Field(default=None, description="Database name or path")
    username: Optional[str] = Field(default=None, description="Username for authentication")
    password: Optional[SecretStr] = Field(default=None, description="Password (stored securely)")
    
    # Additional options
    schema: Optional[str] = Field(default=None, description="Schema name (PostgreSQL)")
    timeout: float = Field(default=30.0, ge=1.0, le=300.0, description="Connection timeout in seconds")
    
    # MongoDB-specific
    uri: Optional[str] = Field(default=None, description="MongoDB URI (alternative to connection_string)")
    
    model_config = {
        "extra": "forbid"  # Reject unknown fields
    }
    
    @field_validator("connection_string", "uri", mode="before")
    @classmethod
    def resolve_env_in_string(cls, v: Optional[str]) -> Optional[str]:
        """Resolve ${ENV_VAR} placeholders in connection strings."""
        if v is None:
            return None
        return resolve_env_vars(v)
    
    @field_validator("password", mode="before")
    @classmethod
    def resolve_env_in_password(cls, v: Any) -> Optional[SecretStr]:
        """Resolve ${ENV_VAR} placeholders in password."""
        if v is None:
            return None
        if isinstance(v, SecretStr):
            resolved = resolve_env_vars(v.get_secret_value())
            return SecretStr(resolved)
        resolved = resolve_env_vars(str(v))
        return SecretStr(resolved)
    
    def get_connection_string(self) -> str:
        """Build or return the connection string for this profile."""
        if self.connection_string:
            return self.connection_string
        
        if self.type == "sqlite":
            # SQLite: sqlite:///path/to/file.db
            return f"sqlite:///{self.database}"
        
        if self.type == "mongodb":
            # MongoDB uses URI
            if self.uri:
                return self.uri
            # Build URI from components
            password = self.password.get_secret_value() if self.password else ""
            auth = f"{self.username}:{password}@" if self.username else ""
            return f"mongodb://{auth}{self.host}:{self.port or 27017}/{self.database}"
        
        # MySQL / PostgreSQL
        password = self.password.get_secret_value() if self.password else ""
        auth = f"{self.username}:{password}@" if self.username else ""
        
        if self.type == "mysql":
            return f"mysql+pymysql://{auth}{self.host}:{self.port or 3306}/{self.database}"
        elif self.type == "postgresql":
            return f"postgresql+psycopg2://{auth}{self.host}:{self.port or 5432}/{self.database}"
        
        raise ValueError(f"Unsupported database type: {self.type}")


class DatabaseConfig(BaseModel):
    """Root configuration containing multiple connection profiles."""
    connections: Dict[str, ConnectionProfile] = Field(
        default_factory=dict,
        description="Named connection profiles"
    )


def resolve_env_vars(value: str) -> str:
    """Resolve ${ENV_VAR} placeholders with environment variable values.
    
    Args:
        value: String potentially containing ${VAR} placeholders
        
    Returns:
        String with all placeholders replaced by their values.
        Missing env vars are replaced with empty string.
        
    Examples:
        >>> os.environ["DB_PASS"] = "secret123"
        >>> resolve_env_vars("${DB_PASS}")
        'secret123'
        >>> resolve_env_vars("prefix_${MISSING}_suffix")
        'prefix__suffix'
    """
    if not value:
        return value
    
    pattern = r'\$\{([^}]+)\}'
    
    def replace(match: re.Match) -> str:
        var_name = match.group(1)
        env_value = os.environ.get(var_name, "")
        if not env_value:
            logger.warning(f"Environment variable '{var_name}' not found, using empty string")
        return env_value
    
    return re.sub(pattern, replace, value)


def load_config(config_path: Optional[str] = None) -> DatabaseConfig:
    """Load database configuration from JSON file.
    
    Auto-discovers db_connections.json if no path provided.
    Searches current directory and parent directories.
    
    Args:
        config_path: Optional path to config file
        
    Returns:
        DatabaseConfig with validated connection profiles
        
    Raises:
        FileNotFoundError: If config file not found
        ValueError: If config validation fails
    """
    if config_path is None:
        config_path = _discover_config_file()
    
    if not Path(config_path).exists():
        raise FileNotFoundError(f"Database config not found: {config_path}")
    
    logger.info(f"Loading database config from: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    # Validate with Pydantic
    config = DatabaseConfig(**raw_data)
    
    # Log loaded profiles (mask credentials)
    for name, profile in config.connections.items():
        masked_conn = _mask_connection_string(profile.get_connection_string())
        logger.info(f"Loaded connection profile '{name}': {profile.type} ({masked_conn})")
    
    return config


def _discover_config_file() -> str:
    """Auto-discover db_connections.json in current or parent directories.
    
    Returns:
        Path to config file
        
    Raises:
        FileNotFoundError: If no config file found
    """
    filename = "db_connections.json"
    
    # Start from current directory
    current = Path.cwd()
    
    # Search current and up to 5 parent directories
    for _ in range(6):
        candidate = current / filename
        if candidate.exists():
            return str(candidate)
        
        parent = current.parent
        if parent == current:  # Reached root
            break
        current = parent
    
    raise FileNotFoundError(
        f"Could not find {filename} in current or parent directories. "
        "Please create a db_connections.json file or specify --config path."
    )


def _mask_connection_string(conn_str: str) -> str:
    """Mask password in connection string for logging.
    
    Args:
        conn_str: Full connection string
        
    Returns:
        Connection string with password replaced by ***
    """
    # Match pattern: user:password@
    pattern = r'(://[^:]+:)([^@]+)(@)'
    return re.sub(pattern, r'\1***\3', conn_str)


# Convenience function for quick profile access
def get_connection(name: str, config_path: Optional[str] = None) -> ConnectionProfile:
    """Get a specific connection profile by name.
    
    Args:
        name: Profile name from config
        config_path: Optional config file path
        
    Returns:
        ConnectionProfile instance
        
    Raises:
        KeyError: If profile name not found
    """
    config = load_config(config_path)
    if name not in config.connections:
        available = list(config.connections.keys())
        raise KeyError(
            f"Connection profile '{name}' not found. "
            f"Available profiles: {available}"
        )
    return config.connections[name]
