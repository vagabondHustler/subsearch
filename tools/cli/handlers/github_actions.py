import os
import uuid


def set_output(name: str, value: str | int | bool) -> None:
    """Append key-value pair to GitHub Actions output.

    Parameters:
        name (str): Name of the output variable.
        value (str | int | bool): Value associated with the output variable.

    Returns:
        None
    """

    with open(os.environ["GITHUB_OUTPUT"], "a") as fh:
        print(f"{name}={value}", file=fh)


def set_multiline_output(name: str, value: str | int | bool) -> None:
    """Append multiline value to GitHub Actions output.

    Parameters:
        name (str): Name of the multiline output variable.
        value (str | int | bool): Multiline value associated with the output variable.

    Returns:
        None
    """

    with open(os.environ["GITHUB_OUTPUT"], "a") as fh:
        delimiter = uuid.uuid1()
        print(f"{name}<<{delimiter}", file=fh)
        print(value, file=fh)
        print(delimiter, file=fh)
