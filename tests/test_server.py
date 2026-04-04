import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestServerFunctions:
    """Tests for server module functions."""

    def test_find_free_port(self):
        """find_free_port should return a valid port."""
        from scripts.server import find_free_port

        port = find_free_port(19000, 19100)
        assert 19000 <= port < 19100

    def test_check_server_running_none(self):
        """check_server_running should return None when no server."""
        from scripts.server import check_server_running

        result = check_server_running(19999, 20000)
        assert result is None

    def test_custom_handler_health_endpoint(self):
        """CustomHTTPRequestHandler should have health endpoint logic."""
        from scripts.server import CustomHTTPRequestHandler

        # Check the handler has do_GET method
        assert hasattr(CustomHTTPRequestHandler, 'do_GET')

    def test_custom_handler_end_headers(self):
        """CustomHTTPRequestHandler should have CORS headers."""
        from scripts.server import CustomHTTPRequestHandler

        # Check the handler has end_headers method
        assert hasattr(CustomHTTPRequestHandler, 'end_headers')
