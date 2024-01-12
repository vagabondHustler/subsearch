from datetime import datetime


def get_timestamp() -> str:
    return datetime.now().strftime("%H:%M:%S")


def verbose_print(text: str, new_line=False) -> None:
    default = f"{text}"
    msg = f"{default}" if not new_line else f"{default}\n"
    print(f"{msg}")
