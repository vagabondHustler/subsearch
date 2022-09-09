import os


class Paths:
    home: str
    data: str
    gui: str
    providers: str
    utils: str
    icon: str
    titlebar: str
    tabs: str


class SetPaths:
    def __init__(self) -> None:
        home = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
        all_paths = {
            "home": home,
            "data": os.path.join(home, "data"),
            "gui": os.path.join(home, "gui"),
            "providers": os.path.join(home, "providers"),
            "utils": os.path.join(home, "utils"),
            "icon": os.path.join(home, "gui", "assets", "icon", "subsearch.ico"),
            "titlebar": os.path.join(home, "gui", "assets", "titlebar"),
            "tabs": os.path.join(home, "gui", "assets", "tabs"),
        }
        for k, v in all_paths.items():
            setattr(Paths, k, v)


class SubsearchPath:
    """base class for subsearch path"""


if __name__ != "__main__":
    __set_values__ = SetPaths()
    __home__: str = getattr(Paths, "home")
    __data__: str = getattr(Paths, "data")
    __gui__: str = getattr(Paths, "gui")
    __providers__: str = getattr(Paths, "providers")
    __utils__: str = getattr(Paths, "utils")
    __icon__: str = getattr(Paths, "icon")
    __titlebar__: str = getattr(Paths, "titlebar")
    __tabs__: str = getattr(Paths, "tabs")
