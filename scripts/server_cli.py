#!/usr/bin/env python3
"""
Server Management CLI for echart-skill.

Provides start, stop, and status commands for managing the local HTTP server.
Service state is persisted to outputs/.server_status.json for restart recovery.
"""

import os
import sys
import json
import signal
import argparse
import subprocess
import time
import fcntl
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import server utilities
try:
    from scripts.server import check_server_running, find_free_port, ServerLifecycle
except ImportError:
    # Fallback for direct execution
    from server import check_server_running, find_free_port, ServerLifecycle

# Constants
STATUS_FILE = Path("outputs/.server_status.json")
STATUS_DIR = STATUS_FILE.parent
SERVER_START_TIMEOUT = 2.0  # seconds
SERVER_STOP_TIMEOUT = 1.0  # seconds
DEFAULT_PORT_RANGE = (8100, 8200)


def load_status() -> dict:
    """Load server status from file.
    
    Returns:
        Status dict, or empty dict if file doesn't exist
    """
    if not STATUS_FILE.exists():
        return {}
    
    try:
        with open(STATUS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_status(status: dict) -> None:
    """Save server status to file.
    
    Args:
        status: Status dict to save
    """
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATUS_FILE, 'w') as f:
        json.dump(status, f, indent=2)


def start_server(port: int | None = None, force_restart: bool = False) -> dict:
    """Start the local HTTP server.
    
    Args:
        port: Optional specific port (default: auto-select from 8100-8200)
        force_restart: If True, always restart even if already running
    
    Returns:
        Status dict with pid, port, start_time, status
    """
    # File lock to prevent concurrent start_server calls
    lock_path = STATUS_DIR / ".start_server.lock"
    STATUS_DIR.mkdir(parents=True, exist_ok=True)
    lock_fd = open(str(lock_path), 'w')
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except (IOError, OSError):
        lock_fd.close()
        return {
            "status": "error",
            "message": "Another start/stop operation is in progress. Please wait."
        }
    
    try:
        # Load existing status to remember previous port
        existing_status = load_status()
        previous_port = existing_status.get("port")
        
        # Check if server already running
        running_port = check_server_running(*DEFAULT_PORT_RANGE)
        
        if running_port:
            # Server is running - stop it first to avoid duplicate instances
            stop_result = stop_server()
            if stop_result.get("status") not in ["stopped", "not_running"]:
                return {
                    "status": "error",
                    "message": f"Failed to stop existing server: {stop_result.get('message')}",
                    "previous_port": running_port
                }
            time.sleep(0.5)
        
        # If no specific port requested, try previous port first (for restart)
        if port is None:
            if previous_port and DEFAULT_PORT_RANGE[0] <= previous_port <= DEFAULT_PORT_RANGE[1]:
                port = previous_port
            else:
                port = None  # Will auto-select
        
        # Find available port
        if port is None:
            try:
                port = find_free_port(*DEFAULT_PORT_RANGE)
            except IOError as e:
                return {
                    "status": "error",
                    "message": f"No available ports in range {DEFAULT_PORT_RANGE[0]}-{DEFAULT_PORT_RANGE[1]}",
                    "error": str(e)
                }
        else:
            import socket
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('', port))
            except OSError:
                try:
                    port = find_free_port(*DEFAULT_PORT_RANGE)
                except IOError as e:
                    return {
                        "status": "error",
                        "message": f"Port {port} not available and no free ports found",
                        "error": str(e)
                    }
        
        # Start server as daemon process
        server_script = Path(__file__).parent / "server.py"
        cmd = [sys.executable, str(server_script), "--daemon", "--port", str(port)]
        
        try:
            if sys.platform == 'win32':
                proc = subprocess.Popen(
                    cmd,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            else:
                proc = subprocess.Popen(
                    cmd,
                    start_new_session=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            
            # Wait for server to start
            start_time = time.time()
            while time.time() - start_time < SERVER_START_TIMEOUT:
                time.sleep(0.1)
                if check_server_running(port, port + 1):
                    break
            else:
                return {
                    "status": "timeout",
                    "message": f"Server failed to start within {SERVER_START_TIMEOUT}s",
                    "port": port
                }
            
            # Save status
            status = {
                "pid": proc.pid,
                "port": port,
                "start_time": datetime.now().isoformat(),
                "status": "running"
            }
            save_status(status)
            
            return status
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to start server process: {str(e)}",
                "error": str(e)
            }
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        lock_fd.close()


def stop_server() -> dict:
    """Stop the local HTTP server.
    
    Returns:
        Status dict indicating stopped or error
    """
    # Load current status
    status = load_status()
    
    if not status or status.get("status") != "running":
        return {
            "status": "not_running",
            "message": "Server is not running"
        }
    
    pid = status.get("pid")
    if pid is None:
        # No PID recorded, check if server is actually running
        port = status.get("port")
        if port and check_server_running(port, port + 1):
            # Server running but no PID - try to find and kill it
            lifecycle = ServerLifecycle(port)
            pid = lifecycle.read_pid()
            if pid:
                status["pid"] = pid
            else:
                # Can't determine PID, just update status
                stopped_status = {
                    "status": "stopped",
                    "stopped_time": datetime.now().isoformat(),
                    "message": "Server stopped (no PID tracking)"
                }
                save_status(stopped_status)
                return stopped_status
    
    # Send SIGTERM to process
    try:
        os.kill(pid, signal.SIGTERM)
        
        # Wait for process to terminate
        start_time = time.time()
        while time.time() - start_time < SERVER_STOP_TIMEOUT:
            time.sleep(0.1)
            try:
                os.kill(pid, 0)  # Check if process still exists
            except (OSError, ProcessLookupError):
                # Process terminated
                break
        else:
            # Timeout, force kill
            try:
                os.kill(pid, signal.SIGKILL)
            except (OSError, ProcessLookupError):
                pass
        
        # Update status
        stopped_status = {
            "status": "stopped",
            "stopped_time": datetime.now().isoformat(),
            "port": status.get("port"),
            "message": "Server stopped successfully"
        }
        save_status(stopped_status)
        
        return stopped_status
        
    except (OSError, ProcessLookupError) as e:
        # Process doesn't exist
        stopped_status = {
            "status": "stopped",
            "stopped_time": datetime.now().isoformat(),
            "port": status.get("port"),
            "message": "Server was not running (process not found)"
        }
        save_status(stopped_status)
        
        return stopped_status
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to stop server: {str(e)}",
            "error": str(e)
        }


def get_status() -> dict:
    """Get current server status.
    
    Returns:
        Status dict with current state
    """
    # Load status file
    status = load_status()
    
    if not status:
        return {
            "status": "never_started",
            "message": "Server has never been started"
        }
    
    # If marked as running, verify process is still active
    if status.get("status") == "running":
        pid = status.get("pid")
        port = status.get("port")
        
        # Check if process exists
        process_alive = False
        if pid:
            try:
                os.kill(pid, 0)
                process_alive = True
            except (OSError, ProcessLookupError):
                process_alive = False
        
        # Check if port is responding
        port_responding = False
        if port:
            port_responding = bool(check_server_running(port, port + 1))
        
        # Update status if server is dead
        if not process_alive and not port_responding:
            status = {
                "status": "stopped",
                "stopped_time": datetime.now().isoformat(),
                "port": port,
                "message": "Server stopped (process died)"
            }
            save_status(status)
        elif not process_alive and port_responding:
            # Port responding but PID mismatch - could be different process
            status["message"] = "Server running (PID unknown)"
    
    return status


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Manage local HTTP server for viewing charts",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Start command
    start_parser = subparsers.add_parser("start", help="Start the local server")
    start_parser.add_argument(
        "--port", type=int,
        help="Port to run on (default: auto-select from 8100-8200)"
    )
    
    # Stop command
    stop_parser = subparsers.add_parser("stop", help="Stop the local server")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Check server status")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    if args.command == "start":
        result = start_server(port=args.port)
    elif args.command == "stop":
        result = stop_server()
    elif args.command == "status":
        result = get_status()
    else:
        result = {"status": "error", "message": f"Unknown command: {args.command}"}
    
    # Output JSON to stdout
    print(json.dumps(result, indent=2))
    
    # Set exit code
    if result.get("status") == "error":
        sys.exit(1)
    elif result.get("status") == "timeout":
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
