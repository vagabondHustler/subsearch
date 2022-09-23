from pathlib import Path

from subsearch.data.data_fields import SubsearchPaths


class SetPaths:
    def __init__(self) -> None:
        home = Path(__file__).resolve().parent.parent
        all_paths = {
            "home": home,
            "data": Path(home) / "data",
            "gui": Path(home) / "gui",
            "providers": Path(home) / "providers",
            "utils": Path(home) / "utils",
            "icon": Path(home) / "gui" / "assets" / "icon" / "subsearch.ico",
            "titlebar": Path(home) / "gui" / "assets" / "titlebar",
            "tabs": Path(home) / "gui" / "assets" / "tabs",
        }
        for k, v in all_paths.items():
            setattr(SubsearchPaths, k, v)


if __name__ != "__main__":
    __set_values__ = SetPaths()
    __home__: str = getattr(SubsearchPaths, "home")
    __data__: str = getattr(SubsearchPaths, "data")
    __gui__: str = getattr(SubsearchPaths, "gui")
    __providers__: str = getattr(SubsearchPaths, "providers")
    __utils__: str = getattr(SubsearchPaths, "utils")
    __icon__: str = getattr(SubsearchPaths, "icon")
    __titlebar__: str = getattr(SubsearchPaths, "titlebar")
    __tabs__: str = getattr(SubsearchPaths, "tabs")
