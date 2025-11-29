import logging
import os
import sys
import time

from luminol.daemon.protocol import print_response_and_exit

from .daemon.client import PID_FILE, SOCKET_FILE, send_request, run, ping, server_stop
from .utils.logging_config import configure_logging
from .cli.parser import parse_daemon_cli_args


def stop_daemon():
    """
    Attempts to gracefully stop the daemon.
    If that fails, falls back to cleaning up stale PID and socket files.
    """

    def cleanup_daemon_files():
        """Forcibly removes the PID and socket files."""
        print("Daemon is not responsive. Cleaning up stale files...")
        cleaned = False
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
            print(f"Removed stale PID file: {PID_FILE}")
            cleaned = True
        if os.path.exists(SOCKET_FILE):
            os.remove(SOCKET_FILE)
            print(f"Removed stale socket file: {SOCKET_FILE}")
            cleaned = True

        if cleaned:
            print("Cleanup complete.")
        else:
            print("No stale files found to clean up.")

    print("Stopping Luminol daemon...")
    try:
        response = send_request(server_stop())
        if response.get("success"):
            print("Daemon stopped successfully.")
        else:
            print(f"Error stopping daemon: {response.get('error', 'Unknown error')}")
            cleanup_daemon_files()

    except (ConnectionRefusedError, FileNotFoundError):
        cleanup_daemon_files()


def handle_start(args):
    """Handles the 'start' command."""
    try:
        if send_request(ping()).get("success"):
            print("Daemon is already running.")
            sys.exit(0)
    except (ConnectionRefusedError, FileNotFoundError):
        pass  # Expected if daemon is not running

    # Intentional lazy load
    from .daemon.server import server_start  # pylint: disable= import-outside-toplevel

    print("Starting Luminol daemon...")
    server_start(debug=args.debug)
    if not args.debug:
        time.sleep(1)  # Give daemon a moment to initialize
        try:
            if send_request(ping()).get("success"):
                print("Daemon has started")
            else:
                print("Daemon failed to start.")
        except (ConnectionRefusedError, FileNotFoundError):
            logging.exception("Daemon failed to start")


def handle_ping():
    """Handles the 'ping' command."""
    try:
        start_time = time.perf_counter()
        response = send_request(ping())
        status_msg = response.get("logs", "")

        if "pong" in status_msg.lower():
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            print(f"{status_msg} (in {duration_ms:.2f}ms)")
        else:
            print(f"Daemon returned an error: {response.get('error', 'Unknown error')}")
    except (ConnectionRefusedError, FileNotFoundError):
        print("Daemon is not running.")
    except Exception:
        logging.exception("An unexpected error occurred")


def handle_run(args):
    """Handles the 'run' command."""
    payload = {
        "image_path": str(args.image),
        "theme_type": args.theme,
        "quality": args.quality,
        "preview_only": args.preview,
        "dry_run_only": args.dry_run,
        "validate_only": args.validate,
        "verbose": args.verbose,
    }

    try:
        response = send_request(run(payload))
        if response.get("success"):
            print_response_and_exit(response)
            print("Luminol run completed successfully.")
        else:
            print_response_and_exit(response)
            print(f"Error: {response.get('error', 'An unknown error occurred')}")
    except (ConnectionRefusedError, FileNotFoundError):
        print("Daemon is not running. Please start it with 'lumid start'.")
        sys.exit(1)
    except Exception:
        logging.exception("Failed to send command to daemon")
        sys.exit(1)


def main():
    """Main entry point for the Luminol daemon client."""
    args = parse_daemon_cli_args()
    configure_logging(verbose=False)

    command_handlers = {
        "start": lambda: handle_start(args),
        "stop": stop_daemon,
        "ping": handle_ping,
        "run": lambda: handle_run(args),
    }

    handler = command_handlers.get(args.command)
    if handler:
        handler()
    else:
        logging.error("No command specified. Use --help to see available commands.")
        sys.exit(1)


if __name__ == "__main__":
    main()
