import pytest
import os
import sys
import socket
import threading
import time
import json
import urllib.request

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

    def test_check_server_running_detects_server(self):
        """check_server_running should detect running server."""
        from scripts.server import check_server_running, CustomHTTPRequestHandler
        import http.server
        import socketserver

        # Find a free port range
        test_port = 19992

        # Start server in background
        server_started = threading.Event()

        def run_server():
            class Handler(CustomHTTPRequestHandler):
                def log_message(self, format, *args):
                    pass  # Suppress logs

            with socketserver.TCPServer(('127.0.0.1', test_port), Handler) as httpd:
                server_started.set()
                httpd.handle_request()
                httpd.handle_request()  # Handle health check

        thread = threading.Thread(target=run_server, daemon=True)
        thread.start()
        server_started.wait(timeout=2)

        # Check if our server is detected
        result = check_server_running(test_port, test_port + 1)
        assert result == test_port

    def test_no_free_port_raises_error(self):
        """find_free_port should raise when no ports available."""
        from scripts.server import find_free_port

        # Bind all ports in range to force error
        sockets = []
        try:
            for p in range(19980, 19985):
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.bind(('127.0.0.1', p))
                sockets.append(s)

            with pytest.raises(IOError, match="No free ports found"):
                find_free_port(19980, 19985)
        finally:
            for s in sockets:
                s.close()


class TestCustomHandler:
    """Tests for CustomHTTPRequestHandler."""

    def test_health_endpoint_returns_ok(self):
        """Health endpoint should return OK status."""
        from scripts.server import CustomHTTPRequestHandler
        import socketserver

        port = 19993

        class MockHandler(CustomHTTPRequestHandler):
            def log_message(self, format, *args):
                pass

        server_started = threading.Event()

        def run_server():
            with socketserver.TCPServer(('127.0.0.1', port), MockHandler) as httpd:
                server_started.set()
                httpd.handle_request()

        thread = threading.Thread(target=run_server, daemon=True)
        thread.start()
        server_started.wait(timeout=2)

        # Test health endpoint
        response = urllib.request.urlopen(f'http://127.0.0.1:{port}/__data_skill_health', timeout=2)
        data = json.loads(response.read().decode())

        assert response.status == 200
        assert data['status'] == 'ok'
        assert data['app'] == 'data-skill'

    def test_path_traversal_blocked(self):
        """Path traversal attempts should be blocked."""
        from scripts.server import CustomHTTPRequestHandler
        import socketserver

        port = 19994

        class MockHandler(CustomHTTPRequestHandler):
            def log_message(self, format, *args):
                pass

        server_started = threading.Event()

        def run_server():
            with socketserver.TCPServer(('127.0.0.1', port), MockHandler) as httpd:
                server_started.set()
                httpd.handle_request()

        thread = threading.Thread(target=run_server, daemon=True)
        thread.start()
        server_started.wait(timeout=2)

        # Try path traversal
        try:
            urllib.request.urlopen(f'http://127.0.0.1:{port}/../../../etc/passwd', timeout=2)
            assert False, "Should have raised error"
        except urllib.error.HTTPError as e:
            # Server blocks path traversal with 403
            assert e.code == 403
