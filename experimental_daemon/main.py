#!/usr/bin/env python3
"""
CLI client that sends functions to the daemon for execution.
Usage: python main.py input.jpg output.jpg --width 800
"""

import socket
import pickle
import sys
import argparse
import inspect

SOCKET_PATH = "/tmp/generic_daemon.sock"
MAX_MESSAGE_SIZE = 100 * 1024 * 1024  # 100MB


def resize_image(input_path, width=None, height=None):
    """
    Resize an image and return the PIL Image object.
    This function will be sent to and executed by the daemon.

    Note: Import statements inside the function for safety.
    """
    import time

    start = time.perf_counter()
    from PIL import Image

    end = time.perf_counter()
    print(f"import time = {end - start}")

    img = Image.open(input_path)

    # Calculate dimensions if only one is provided
    if width and not height:
        ratio = width / img.width
        height = int(img.height * ratio)
    elif height and not width:
        ratio = height / img.height
        width = int(img.width * ratio)
    elif not width and not height:
        raise ValueError("Must provide at least width or height")

    resized = img.resize((width, height), Image.Resampling.LANCZOS)
    return resized


def send_function_to_daemon(func, *args, **kwargs):
    """
    Send a function to the daemon for execution and get the result.

    Args:
        func: The function to execute
        *args: Positional arguments for the function
        **kwargs: Keyword arguments for the function

    Returns:
        The result from executing the function
    """
    try:
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(SOCKET_PATH)

        # Get the function source code
        func_code = inspect.getsource(func)

        # Rename the function to 'user_function' for the daemon
        func_name = func.__name__
        func_code = func_code.replace(f"def {func_name}(", "def user_function(", 1)

        # Prepare request
        request = {"function_code": func_code, "args": args, "kwargs": kwargs}

        # Send request
        data = pickle.dumps(request)
        client.sendall(data)
        client.shutdown(socket.SHUT_WR)

        # Receive response
        response_data = b""
        while True:
            chunk = client.recv(4096)
            if not chunk:
                break
            response_data += chunk
            if len(response_data) >= MAX_MESSAGE_SIZE:
                raise ValueError("Response too large")

        client.close()
        response = pickle.loads(response_data)

        if response["success"]:
            # Print any captured logs from the daemon
            if "logs" in response and response["logs"]:
                print(response["logs"], end="")  # end='' avoids extra newline

            return response["result"]
        else:
            print(f"Error from daemon: {response['error']}")
            if "traceback" in response:
                print(response["traceback"])
            sys.exit(1)

    except FileNotFoundError:
        print("Error: Daemon not running. Start it with: python daemon.py")
        sys.exit(1)
    except Exception as e:
        print(f"Error communicating with daemon: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Resize images quickly using daemon")
    parser.add_argument("input", help="Input image path")
    parser.add_argument("output", help="Output image path")
    parser.add_argument("--width", type=int, help="Target width")
    parser.add_argument("--height", type=int, help="Target height")

    args = parser.parse_args()

    if not args.width and not args.height:
        print("Error: Must specify at least --width or --height")
        sys.exit(1)

    print(f"Sending resize function to daemon...")

    # Send the resize_image function to daemon and get the Image object back
    img_object = send_function_to_daemon(
        resize_image, args.input, width=args.width, height=args.height
    )

    # Save the returned Image object to file
    print(f"Saving image to {args.output}...")
    img_object.save(args.output)

    print(f"✓ Image saved successfully!")
    print(f"  Size: {img_object.width}x{img_object.height}")


if __name__ == "__main__":
    main()
