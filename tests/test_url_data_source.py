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
