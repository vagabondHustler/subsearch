from datetime import datetime


def get_timestamp() -> str:
    """
    Get the current timestamp in the "Hour:Minute:Second" format.

    Returns:
        str: The formatted timestamp.
    """
    return datetime.now().strftime("%H:%M:%S")


def verbose_print(text: str | int | bool, new_line=False) -> str:
    """
    Create a verbose message with a timestamp.

    Args:
        text (str | int | bool): The content of the message.
        new_line (bool, optional): If True, append a newline at the end. Defaults to False.

    Returns:
        str: The verbose message.
    """
    default = f"{get_timestamp()} - {msg}"
    msg = f"{default}" if not new_line else f"{default}\n"
    return msg



