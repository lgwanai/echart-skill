import os
import sys
import json
import threading
import http.server
import socketserver
import socket
import argparse
import urllib.request
import urllib.error

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logging_config import get_logger, configure_logging

# Initialize logging
configure_logging()
logger = get_logger(__name__)

def find_free_port(start_port=8100, max_port=8200):
    for port in range(start_port, max_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('', port))
                return port
            except OSError:
                continue
    raise IOError("No free ports found")

def check_server_running(start_port=8100, max_port=8200):
    """Check if the data-skill server is already running by probing ports."""
    for port in range(start_port, max_port):
        is_open = False
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.1)
            if s.connect_ex(('127.0.0.1', port)) == 0:
                is_open = True
                
        if is_open:
            # Port is in use, check if it's our server
            try:
                req = urllib.request.Request(f"http://127.0.0.1:{port}/__data_skill_health")
                with urllib.request.urlopen(req, timeout=1.0) as response:
                    if response.status == 200:
                        data = json.loads(response.read().decode())
                        if data.get("app") == "data-skill":
                            return port
            except Exception:
                pass
    return None

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/__data_skill_health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "app": "data-skill"}).encode())
            return
        super().do_GET()

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()
        
    def log_message(self, format, *args):
        logger.debug("HTTP request", method=self.command, path=self.path)

def run_server_forever(port, base_dir):
    """Run the server synchronously."""
    os.chdir(base_dir)
    handler = CustomHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass

def ensure_server_running():
    """
    Ensures a lightweight HTTP server is running to serve the generated charts.
    Returns the base URL.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    port = check_server_running()
    
    if not port:
        import subprocess
        port = find_free_port()
        
        # Start this very script as a background process using the --daemon flag
        cmd = [sys.executable, os.path.abspath(__file__), "--daemon", "--port", str(port)]
        
        if sys.platform == 'win32':
            subprocess.Popen(cmd, 
                             creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.Popen(cmd, 
                             start_new_session=True,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                             
        # Wait a moment for it to start
        import time
        for _ in range(10):
            time.sleep(0.2)
            if check_server_running(port, port + 1):
                break
                
    return f"http://127.0.0.1:{port}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Data Skill local HTTP server")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    parser.add_argument("--port", type=int, help="Port to run on")
    
    args = parser.parse_args()
    
    if args.daemon and args.port:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logger.info("启动本地服务器", port=args.port)
        run_server_forever(args.port, base_dir)
    else:
        url = ensure_server_running()
        logger.info("服务器已启动", url=url)