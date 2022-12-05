from pathlib import Path

from subsearch.data.data_objects import AppPaths


def get_paths() -> AppPaths:
    home = Path(__file__).resolve().parent.parent
    return AppPaths(
        home=home,
        data=Path(home) / "data",
        gui=Path(home) / "gui",
        providers=Path(home) / "providers",
        utils=Path(home) / "utils",
        icon=Path(home) / "gui" / "assets" / "icon" / "subsearch.ico",
        tabs=Path(home) / "gui" / "assets" / "tabs",
    )


__paths__ = get_paths()
