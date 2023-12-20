import re
from pathlib import Path

from tools.cli.globals import VERSION_PATTERN, VERSION_PYTON_PATH


def read_string(**kwargs) -> str:
    """
    Retrieves information from a specified file using a regex pattern.

    Args:
        file (Path, optional): The path to the file. Defaults to VERSION_PYTHON_PATH.
        pattern (str, optional): The regex pattern to search for. Defaults to VERSION_REGEX_PATTERN.

    Returns:
        str: The matched version string.
    """
    file = kwargs.get("file", VERSION_PYTON_PATH)
    pattern = kwargs.get("pattern", VERSION_PATTERN)
    with open(file, "r") as f:
        file_content = f.read()
        pattern_ = re.compile(pattern)
        match = re.search(pattern_, file_content)

        if match:
            version = match.group(0)  # type: ignore
            return version
        else:
            raise AttributeError(f"No match found in file {file} using pattern {pattern}")


def write_string(file: Path, pattern: str, write_string: str) -> None:
    """
    Updates the specified file with a new string using a regex pattern.

    Args:
        file (Path): The path to the file.
        pattern (str): The regex pattern to search for.
        write_string (str): The new string to replace the matched pattern.
    """
    with open(file, "r") as f:
        file_content = f.read()
        pattern_ = re.compile(pattern)
        updated_content = re.sub(pattern_, write_string, file_content)

    with open(file, "w") as f:
        f.write(updated_content)
