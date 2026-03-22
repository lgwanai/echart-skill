import os
import sys
import json
import threading
import http.server
import socketserver
import socket
from urllib.parse import urlparse

def find_free_port(start_port=8000, max_port=8100):
    for port in range(start_port, max_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('', port))
                return port
            except OSError:
                continue
    raise IOError("No free ports found")

def get_server_info_file():
    """Get the path to the server info file."""
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tmp', '.server_info')

def check_server_running():
    """Check if the server is already running."""
    info_file = get_server_info_file()
    if not os.path.exists(info_file):
        return None
        
    try:
        with open(info_file, 'r') as f:
            info = json.load(f)
            port = info.get('port')
            
            # Simple check if port is in use
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                result = s.connect_ex(('127.0.0.1', port))
                if result == 0:
                    return port
    except Exception:
        pass
        
    # If file exists but server is not running or file is corrupted, remove it
    try:
        os.remove(info_file)
    except:
        pass
    return None

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()
        
    def log_message(self, format, *args):
        # Suppress logging to keep console clean
        pass

def start_server_in_background(base_dir):
    """Start the HTTP server in a background thread."""
    # Ensure tmp directory exists
    os.makedirs(os.path.join(base_dir, 'tmp'), exist_ok=True)
    
    port = check_server_running()
    if port:
        return port
        
    port = find_free_port()
    
    # Save server info
    with open(get_server_info_file(), 'w') as f:
        json.dump({'port': port}, f)
        
    def run_server():
        os.chdir(base_dir) # Server from root to access both tmp/ and assets/
        handler = CustomHTTPRequestHandler
        with socketserver.TCPServer(("", port), handler) as httpd:
            httpd.serve_forever()
            
    # Start thread as daemon so it exits when main process exits
    # But since we want it to persist, we actually just fork it in a real scenario
    # For now, we'll start it as a daemon thread in the current process
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    return port

def ensure_server_running():
    """
    Ensures a lightweight HTTP server is running to serve the generated charts.
    Returns the base URL.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    port = check_server_running()
    
    if not port:
        # We need to spawn a background process so it survives this script's termination
        import subprocess
        
        # Create a simple server script
        server_script = os.path.join(base_dir, 'tmp', '_run_server.py')
        os.makedirs(os.path.join(base_dir, 'tmp'), exist_ok=True)
        
        port = find_free_port()
        
        with open(server_script, 'w') as f:
            f.write(f"""
import http.server
import socketserver
import os
import json

os.chdir('{base_dir}')
PORT = {port}

with open('tmp/.server_info', 'w') as f:
    json.dump({{'port': PORT}}, f)

Handler = http.server.SimpleHTTPRequestHandler
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    httpd.serve_forever()
""")
        
        # Start detached process
        if sys.platform == 'win32':
            subprocess.Popen([sys.executable, server_script], 
                             creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.Popen([sys.executable, server_script], 
                             start_new_session=True,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                             
        # Wait a moment for it to start
        import time
        time.sleep(0.5)
        
    return f"http://127.0.0.1:{port}"

if __name__ == "__main__":
    url = ensure_server_running()
    print(f"Server is running at {url}")