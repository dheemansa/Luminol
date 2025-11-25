import json
from pathlib import Path

RUNTIME_DIR = Path("/tmp") / "luminol"
PID_FILE = RUNTIME_DIR / "luminol.pid"
SOCKET_FILE = RUNTIME_DIR / "luminol.sock"


def response_to_client(success: bool, logs: str, error: str | None = None) -> str:
    response: dict = {"success": success, "logs": logs, "error": error}
    json_response: str = json.dumps(response) + "\n"
    return json_response


def request_to_server(action: str, payload: dict | None = None) -> str:
    SUPPORTED_ACTIONS = ("run", "ping", "stop")
    if action not in SUPPORTED_ACTIONS:
        raise ValueError(
            f"{action}  is no a valid action. Supported actions are {' ,'.join(SUPPORTED_ACTIONS)}"
        )
    request: dict = {"action": action, "payload": payload}
    json_request: str = json.dumps(request) + "\n"

    return json_request


def print_response_and_exit(response: dict):
    success = response.get("success")
    logs = response.get("logs")
    error = response.get("error")

    if error:
        print(f"Error:\n{error}")
    if logs:
        print(logs)

    if success:
        raise SystemExit(0)
    else:
        raise SystemExit(1)
