import logging
from pathlib import Path

from .path import _expand_path


def write_file(file_path: str, content: str | list[str]) -> Path | None:
    """
    Writes content to a specified file path.
    This function handles path expansion (e.g., '~' for home directory)
    and ensures that the parent directories for the file exist before
    writing.
    Args:
        file_path (str): The path to the file to be written. Can contain '~'.
        content (str | list[str]): The content to write. If a list, each element
                                    is treated as a line.
    Returns:
        Path | None: The path to the written file on success, or None on failure.
    """
    try:
        # Use the helper from path.py to expand the file path
        output_path = _expand_path(file_path)
        # Create parent directories if they don't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert list to string if needed
        if isinstance(content, list):
            content = "\n".join(content)

        # Write the content
        output_path.write_text(content, encoding="utf-8")
        logging.info("Successfully wrote file to: %s", output_path)
        return output_path
    except IOError as e:
        logging.error("Failed to write file at %s: %s", file_path, e)
        return None
    except Exception as e:
        logging.error(
            "An unexpected error occurred while writing to %s: %s", file_path, e
        )
        return None
