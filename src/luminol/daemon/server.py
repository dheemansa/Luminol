import socket
import json
import os
import sys
import io
import contextlib

from .protocol import response_to_client, RUNTIME_DIR, PID_FILE, SOCKET_FILE
from ..cli.term_colors import AnsiColors as AC

from PIL import Image
import numpy as np

# ensure both PIL and numpy are initialised
Image.init()
np.array([])


from ..core.engine import run_luminol


def daemonize():
    """Detach the process from the terminal and run in the background."""
    # First fork
    if os.fork() > 0:
        sys.exit(0)

    os.setsid()

    # Second fork
    if os.fork() > 0:
        sys.exit(0)

    # Redirect standard file descriptors
    sys.stdout.flush()
    sys.stderr.flush()
    with open("/dev/null", "rb", 0) as f:
        os.dup2(f.fileno(), sys.stdin.fileno())
    with open("/dev/null", "ab", 0) as f:
        os.dup2(f.fileno(), sys.stdout.fileno())
        os.dup2(f.fileno(), sys.stderr.fileno())


def handle_request(request: dict) -> tuple[str, bool]:
    """
    Returns a Tuple: (JSON_Response_String, Should_Stop_Boolean)
    """
    action: str | None = request.get("action", None)
    should_stop = False
    if action == "run":
        error = None
        success = False
        capture = io.StringIO()
        params = request.get("payload", {})
        with contextlib.redirect_stdout(capture), contextlib.redirect_stderr(capture):
            try:
                run_luminol(
                    image_path=params.get("image_path"),
                    theme_type=params.get("theme_type"),
                    quality=params.get("quality"),
                    preview_only=params.get("preview_only", False),
                    validate_only=params.get("validate_only", False),
                    dry_run_only=params.get("dry_run_only", False),
                    verbose=params.get("verbose", False),
                )
                success = True

            except SystemExit as e:
                if e.code == 0:
                    success = True
                else:
                    success = False
            except Exception as e:
                success = False
                error = (
                    f"Unexpected error occured while executing Luminol in server: {e}"
                )

        logs = capture.getvalue()
        response = response_to_client(success=success, logs=logs, error=error)

    elif action == "stop":
        should_stop = True
        response = response_to_client(success=True, logs="Server Stopped", error=None)

    elif action == "ping":
        response = response_to_client(success=True, logs="Pong!! :)", error=None)

    else:
        response = response_to_client(
            success=False, logs=f"Invalid request: {request}", error=None
        )

    return response, should_stop


def server_start(debug: bool = False):
    # if debug is enabled then keep the server running in the terminal
    if os.path.exists(SOCKET_FILE):
        print("Daemon is already running.")
        return

    if not debug:
        daemonize()

    os.makedirs(RUNTIME_DIR, exist_ok=True)
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(str(SOCKET_FILE))
    server.listen(1)

    print("Waiting for connection...")
    try:
        while True:
            conn, _ = server.accept()
            print("Connection established")

            with conn.makefile("r", encoding="utf-8") as stream:
                print("Waiting for data...")

                # readline() will freeze here until it sees a '\n' character.
                raw_request = stream.readline()
                if not raw_request:
                    print(f"{AC.WARNING}Server sent empty response.{AC.RESET}")

                try:
                    request = json.loads(raw_request)
                    print(
                        f"{AC.INFO}Request from client:{AC.RESET} \n"
                        f"{json.dumps(request, indent=4)}\n"
                    )

                    response, should_stop = handle_request(request)

                    # Pretty-print the response for the server log
                    try:
                        response_dict = json.loads(response)
                        print(
                            f"{AC.INFO}Response to client:{AC.RESET} \n"
                            f"{json.dumps(response_dict, indent=4)}\n"
                        )
                    except json.JSONDecodeError:
                        # If for some reason the response isn't valid JSON, print it raw.
                        print(
                            f"{AC.ERROR}Unexpected bad json response to client (raw): {AC.RESET}\n{response}\n"
                        )

                    conn.sendall(response.encode("utf-8"))

                    if should_stop:
                        print("Stop command received. Exiting loop.")
                        break

                except json.JSONDecodeError:
                    print(
                        f"{AC.ERROR}Bad json request from client (raw):{AC.RESET} \n{raw_request}\n"
                    )
                    # Send raw error if JSON is bad
                    err_resp = response_to_client(
                        success=False,
                        logs=f"Bad json request: {raw_request}",
                        error="Invalid JSON",
                    )
                    conn.sendall(err_resp.encode("utf-8"))

    except KeyboardInterrupt:
        print("\nStoping Daemon")

    finally:
        # cleanup
        server.close()
        if os.path.exists(SOCKET_FILE):
            os.remove(SOCKET_FILE)
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
