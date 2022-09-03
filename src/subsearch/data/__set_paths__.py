import os


class Paths:
    home: str
    data: str
    gui: str
    providers: str
    utils: str
    icons: str
    buttons: str
    tabs: str


class SetPaths:
    def __init__(self) -> None:
        home = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
        all_paths = {
            "home": home,
            "data": os.path.join(home, "data"),
            "gui": os.path.join(home, "gui"),
            "scraper": os.path.join(home, "scraper"),
            "utils": os.path.join(home, "utils"),
            "icons": os.path.join(home, "assets", "icons"),
            "buttons": os.path.join(home, "assets", "buttons"),
            "tabs": os.path.join(home, "assets", "tabs"),
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
    __providers__: str = getattr(Paths, "scraper")
    __utils__: str = getattr(Paths, "utils")
    __icons__: str = getattr(Paths, "icons")
    __buttons__: str = getattr(Paths, "buttons")
    __tabs__: str = getattr(Paths, "tabs")
