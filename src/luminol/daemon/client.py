import json
import logging
import os
import socket
from typing import Any

from .protocol import request_to_server
from .protocol import PID_FILE, SOCKET_FILE


def send_request(request: str) -> dict[str, Any]:
    if not os.path.exists(PID_FILE):
        raise ConnectionRefusedError("Daemon not running (PID file missing)")

    if not os.path.exists(SOCKET_FILE):
        # PID file exists but socket is gone, indicates a stale PID file
        # or a daemon that crashed without cleaning up.
        raise FileNotFoundError("Daemon socket missing. The daemon may have crashed.")

    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        client.connect(str(SOCKET_FILE))
        client.sendall(request.encode("utf-8"))

        with client.makefile("r", encoding="utf-8") as stream:
            # readline() waits for the server's newline
            raw_response = stream.readline()
            if not raw_response:
                logging.warning("Server sent empty response")

            try:
                response: dict = json.loads(raw_response)
                logging.debug("Server replied: %s", response)

            except json.JSONDecodeError:
                # Send raw error if JSON is bad
                logging.exception(f"Bad json response: {raw_response}")
                raise

            return response

    finally:
        client.close()


def run(payload: dict) -> str:
    request: str = request_to_server(action="run", payload=payload)
    return request


def server_stop() -> str:
    request: str = request_to_server(action="stop")
    return request


def ping() -> str:
    request: str = request_to_server(action="ping")
    return request
