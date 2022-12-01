from pathlib import Path

from subsearch.data.metadata_classes import ApplicationPaths


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
            "tabs": Path(home) / "gui" / "assets" / "tabs",
        }
        for k, v in all_paths.items():
            setattr(ApplicationPaths, k, v)


if __name__ != "__main__":
    __set_values__ = SetPaths()
    __home__: str = getattr(ApplicationPaths, "home")
    __data__: str = getattr(ApplicationPaths, "data")
    __gui__: str = getattr(ApplicationPaths, "gui")
    __providers__: str = getattr(ApplicationPaths, "providers")
    __utils__: str = getattr(ApplicationPaths, "utils")
    __icon__: str = getattr(ApplicationPaths, "icon")
    __tabs__: str = getattr(ApplicationPaths, "tabs")
