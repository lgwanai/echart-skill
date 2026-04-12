"""Tests for database configuration module."""

import json
import os
import tempfile
from pathlib import Path

import pytest

from scripts.db_config import (
    DatabaseConfig,
    ConnectionProfile,
    load_config,
    resolve_env_vars,
    get_connection,
    _mask_connection_string,
)


class TestResolveEnvVars:
    """Tests for resolve_env_vars function."""
    
    def test_resolve_single_var(self, monkeypatch):
        """Resolve a single ${VAR} placeholder."""
        monkeypatch.setenv("TEST_VAR", "test_value")
        result = resolve_env_vars("${TEST_VAR}")
        assert result == "test_value"
    
    def test_resolve_multiple_vars(self, monkeypatch):
        """Resolve multiple placeholders in one string."""
        monkeypatch.setenv("HOST", "localhost")
        monkeypatch.setenv("PORT", "3306")
        result = resolve_env_vars("host=${HOST}, port=${PORT}")
        assert result == "host=localhost, port=3306"
    
    def test_missing_var_returns_empty(self, monkeypatch):
        """Missing env vars are replaced with empty string."""
        monkeypatch.delenv("NONEXISTENT_VAR", raising=False)
        result = resolve_env_vars("prefix_${NONEXISTENT_VAR}_suffix")
        assert result == "prefix__suffix"
    
    def test_no_placeholders(self):
        """String without placeholders is unchanged."""
        result = resolve_env_vars("plain_string")
        assert result == "plain_string"
    
    def test_empty_string(self):
        """Empty string returns empty."""
        result = resolve_env_vars("")
        assert result == ""
    
    def test_embedded_in_path(self, monkeypatch):
        """Resolve embedded in a file path."""
        monkeypatch.setenv("HOME", "/Users/testuser")
        result = resolve_env_vars("${HOME}/data/file.db")
        assert result == "/Users/testuser/data/file.db"


class TestConnectionProfile:
    """Tests for ConnectionProfile model."""
    
    def test_sqlite_with_path(self):
        """SQLite profile with database path."""
        profile = ConnectionProfile(type="sqlite", database="/path/to/db.sqlite")
        assert profile.type == "sqlite"
        assert profile.database == "/path/to/db.sqlite"
    
    def test_mysql_with_individual_fields(self):
        """MySQL profile with host, port, username, password."""
        profile = ConnectionProfile(
            type="mysql",
            host="localhost",
            port=3306,
            database="mydb",
            username="user",
            password="secret"
        )
        assert profile.host == "localhost"
        assert profile.port == 3306
        assert profile.database == "mydb"
    
    def test_connection_string_resolution(self, monkeypatch):
        """Connection string ${VAR} is resolved."""
        monkeypatch.setenv("DB_PASS", "mypassword")
        profile = ConnectionProfile(
            type="mysql",
            connection_string="mysql://user:${DB_PASS}@localhost/db"
        )
        conn_str = profile.get_connection_string()
        assert "mypassword" in conn_str
        assert "${DB_PASS}" not in conn_str
    
    def test_password_env_resolution(self, monkeypatch):
        """Password field ${VAR} is resolved."""
        monkeypatch.setenv("DB_PASS", "secret123")
        profile = ConnectionProfile(
            type="postgresql",
            host="localhost",
            database="testdb",
            username="admin",
            password="${DB_PASS}"
        )
        # Password should be resolved
        assert profile.password.get_secret_value() == "secret123"
    
    def test_password_is_secret_str(self):
        """Password is stored as SecretStr."""
        profile = ConnectionProfile(
            type="mysql",
            host="localhost",
            database="db",
            password="secret"
        )
        assert isinstance(profile.password, type(profile.password))
        # str() should not reveal password
        assert "secret" not in str(profile)
    
    def test_get_connection_string_sqlite(self):
        """Build SQLite connection string."""
        profile = ConnectionProfile(type="sqlite", database="/tmp/test.db")
        conn_str = profile.get_connection_string()
        assert conn_str == "sqlite:////tmp/test.db"
    
    def test_get_connection_string_mysql(self):
        """Build MySQL connection string with pymysql driver."""
        profile = ConnectionProfile(
            type="mysql",
            host="db.example.com",
            port=3307,
            database="production",
            username="app_user",
            password="pass123"
        )
        conn_str = profile.get_connection_string()
        assert "mysql+pymysql://" in conn_str
        assert "app_user:pass123@db.example.com:3307/production" in conn_str
    
    def test_get_connection_string_postgresql(self):
        """Build PostgreSQL connection string with psycopg2 driver."""
        profile = ConnectionProfile(
            type="postgresql",
            host="localhost",
            database="analytics",
            username="reader",
            password="reader_pass"
        )
        conn_str = profile.get_connection_string()
        assert "postgresql+psycopg2://" in conn_str
        assert "reader:reader_pass@localhost:5432/analytics" in conn_str
    
    def test_get_connection_string_mongodb_uri(self):
        """MongoDB uses URI."""
        profile = ConnectionProfile(
            type="mongodb",
            uri="mongodb://localhost:27017/mydb"
        )
        conn_str = profile.get_connection_string()
        assert conn_str == "mongodb://localhost:27017/mydb"
    
    def test_default_timeout(self):
        """Default timeout is 30 seconds."""
        profile = ConnectionProfile(type="sqlite", database=":memory:")
        assert profile.timeout == 30.0
    
    def test_invalid_type_rejected(self):
        """Invalid database type is rejected."""
        with pytest.raises(Exception):  # Pydantic validation error
            ConnectionProfile(type="oracle", database="db")
    
    def test_extra_fields_rejected(self):
        """Extra fields are rejected."""
        with pytest.raises(Exception):  # Pydantic validation error
            ConnectionProfile(type="sqlite", database="db", unknown_field="value")


class TestDatabaseConfig:
    """Tests for DatabaseConfig model."""
    
    def test_empty_config(self):
        """Config can be empty."""
        config = DatabaseConfig()
        assert config.connections == {}
    
    def test_single_connection(self):
        """Config with single connection."""
        config = DatabaseConfig(
            connections={
                "main": ConnectionProfile(type="sqlite", database="main.db")
            }
        )
        assert "main" in config.connections
        assert config.connections["main"].type == "sqlite"
    
    def test_multiple_connections(self):
        """Config with multiple connections."""
        config = DatabaseConfig(
            connections={
                "sqlite_local": ConnectionProfile(type="sqlite", database="local.db"),
                "mysql_prod": ConnectionProfile(
                    type="mysql",
                    host="prod.example.com",
                    database="production"
                )
            }
        )
        assert len(config.connections) == 2
        assert "sqlite_local" in config.connections
        assert "mysql_prod" in config.connections


class TestLoadConfig:
    """Tests for load_config function."""
    
    def test_load_valid_config(self, tmp_path):
        """Load a valid config file."""
        config_file = tmp_path / "db_connections.json"
        config_file.write_text(json.dumps({
            "connections": {
                "test_db": {
                    "type": "sqlite",
                    "database": "/tmp/test.db"
                }
            }
        }))
        
        config = load_config(str(config_file))
        assert "test_db" in config.connections
        assert config.connections["test_db"].type == "sqlite"
    
    def test_load_config_with_env_vars(self, tmp_path, monkeypatch):
        """Config with ${VAR} placeholders are resolved."""
        monkeypatch.setenv("DB_PASSWORD", "secret123")
        
        config_file = tmp_path / "db_connections.json"
        config_file.write_text(json.dumps({
            "connections": {
                "mysql_prod": {
                    "type": "mysql",
                    "host": "localhost",
                    "database": "production",
                    "username": "app",
                    "password": "${DB_PASSWORD}"
                }
            }
        }))
        
        config = load_config(str(config_file))
        assert config.connections["mysql_prod"].password.get_secret_value() == "secret123"
    
    def test_file_not_found(self):
        """Raises FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            load_config("/nonexistent/path/config.json")
    
    def test_invalid_json(self, tmp_path):
        """Raises error for invalid JSON."""
        config_file = tmp_path / "db_connections.json"
        config_file.write_text("{ invalid json }")
        
        with pytest.raises(Exception):
            load_config(str(config_file))
    
    def test_auto_discovery(self, tmp_path, monkeypatch):
        """Auto-discover config in current directory."""
        config_file = tmp_path / "db_connections.json"
        config_file.write_text(json.dumps({
            "connections": {
                "auto_found": {
                    "type": "sqlite",
                    "database": ":memory:"
                }
            }
        }))
        
        # Change to temp directory
        original_cwd = Path.cwd()
        monkeypatch.chdir(tmp_path)
        
        try:
            config = load_config()
            assert "auto_found" in config.connections
        finally:
            monkeypatch.chdir(original_cwd)


class TestMaskConnectionString:
    """Tests for _mask_connection_string function."""
    
    def test_mask_mysql_password(self):
        """Mask password in MySQL connection string."""
        conn_str = "mysql://user:secretpass@localhost:3306/db"
        masked = _mask_connection_string(conn_str)
        assert "secretpass" not in masked
        assert "***" in masked
        assert "user" in masked
        assert "localhost" in masked
    
    def test_mask_postgresql_password(self):
        """Mask password in PostgreSQL connection string."""
        conn_str = "postgresql://admin:admin123@db.example.com/mydb"
        masked = _mask_connection_string(conn_str)
        assert "admin123" not in masked
        assert "***" in masked
    
    def test_no_password(self):
        """Connection string without password."""
        conn_str = "sqlite:////path/to/file.db"
        masked = _mask_connection_string(conn_str)
        assert masked == conn_str


class TestGetConnection:
    """Tests for get_connection convenience function."""
    
    def test_get_existing_connection(self, tmp_path):
        """Get an existing connection profile."""
        config_file = tmp_path / "db_connections.json"
        config_file.write_text(json.dumps({
            "connections": {
                "my_sqlite": {
                    "type": "sqlite",
                    "database": "/tmp/test.db"
                }
            }
        }))
        
        profile = get_connection("my_sqlite", str(config_file))
        assert profile.type == "sqlite"
    
    def test_get_nonexistent_connection(self, tmp_path):
        """Raise KeyError for nonexistent profile."""
        config_file = tmp_path / "db_connections.json"
        config_file.write_text(json.dumps({"connections": {}}))
        
        with pytest.raises(KeyError) as exc_info:
            get_connection("nonexistent", str(config_file))
        
        assert "nonexistent" in str(exc_info.value)
        assert "Available profiles" in str(exc_info.value)
