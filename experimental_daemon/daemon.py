#!/usr/bin/env python3
"""
Generic daemon server that executes functions sent by clients.
The daemon pre-imports heavy libraries and executes arbitrary functions.
Usage: python daemon.py
"""

import socket
import pickle
import sys
from pathlib import Path

# Pre-import heavy dependencies
from PIL import Image

SOCKET_PATH = "/tmp/generic_daemon.sock"
MAX_MESSAGE_SIZE = 100 * 1024 * 1024  # 100MB


def execute_function(func_code, func_args, func_kwargs):
    """
    Execute a function sent by the client.

    Args:
        func_code: String containing the function code
        func_args: Tuple of positional arguments
        func_kwargs: Dict of keyword arguments

    Returns:
        Dict with result and captured logs
    """
    from io import StringIO

    # Create a namespace with pre-imported modules
    namespace = {
        "Image": Image,
        # Add other pre-imported modules here as needed
    }

    # Execute the function code in the namespace
    exec(func_code, namespace)

    # Get the function from the namespace (assumes function is named 'user_function')
    func = namespace["user_function"]

    # Capture stdout to get print statements
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    try:
        # Execute the function with provided arguments
        result = func(*func_args, **func_kwargs)

        # Get captured logs
        logs = sys.stdout.getvalue()
    finally:
        # Always restore stdout
        sys.stdout = old_stdout

    return {"result": result, "logs": logs}


def handle_request(request):
    """Handle incoming request."""
    try:
        func_code = request["function_code"]
        func_args = request.get("args", ())
        func_kwargs = request.get("kwargs", {})

        result_data = execute_function(func_code, func_args, func_kwargs)

        return {
            "success": True,
            "result": result_data["result"],
            "logs": result_data["logs"],
        }
    except Exception as e:
        import traceback

        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}


def start_daemon():
    """Start the daemon server."""
    # Remove existing socket if it exists
    socket_path = Path(SOCKET_PATH)
    if socket_path.exists():
        socket_path.unlink()

    # Create Unix socket
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCKET_PATH)
    server.listen(1)

    print(f"Daemon started. Listening on {SOCKET_PATH}")
    print("Pillow pre-imported and ready!")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            conn, _ = server.accept()
            try:
                # Receive data
                data = b""
                while True:
                    chunk = conn.recv(4096)
                    if not chunk:
                        break
                    data += chunk
                    if len(data) >= MAX_MESSAGE_SIZE:
                        raise ValueError("Message too large")

                if data:
                    request = pickle.loads(data)
                    result = handle_request(request)
                    response = pickle.dumps(result)
                    conn.sendall(response)
            finally:
                conn.close()
    except KeyboardInterrupt:
        print("\nShutting down daemon...")
    finally:
        server.close()
        if socket_path.exists():
            socket_path.unlink()


if __name__ == "__main__":
    start_daemon()
