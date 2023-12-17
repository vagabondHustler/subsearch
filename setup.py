import sys
from pathlib import Path

sys.path.insert(0, Path("tools").resolve().parent.as_posix())


def setup():
    from tools import setup_logic

    setup_logic.logic()


if __name__ == "__main__":
    setup()
