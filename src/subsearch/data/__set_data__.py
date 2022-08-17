import os
import sys
from itertools import product


class Paths:
    root: str
    data: str
    gui: str
    scraper: str
    utils: str
    icons: str
    buttons: str


class VideoFile:
    name: str
    ext: str
    path: str
    directory: str


class SetValues:
    def __init__(self) -> None:
        self._video()
        self._paths()

    def _paths(self) -> None:
        """
        Set all the paths SubSearch uses

        Returns:
            Paths: root, data, gui, scraper, utils, icons, buttons
        """
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
        all_paths = {
            "root": root,
            "data": os.path.join(root, "data"),
            "gui": os.path.join(root, "gui"),
            "scraper": os.path.join(root, "scraper"),
            "utils": os.path.join(root, "utils"),
            "icons": os.path.join(root, "assets", "icons"),
            "buttons": os.path.join(root, "assets", "buttons"),
        }
        for k, v in all_paths.items():
            setattr(Paths, k, v)

    def _video(self) -> None:
        """
        Set path, name, directory and ext for the video file

        Returns:
            VideoFilePaths: name, ext, path, directory
        """
        exts = [
            ".avi",
            ".mp4",
            ".mkv",
            ".mpg",
            ".mpeg",
            ".mov",
            ".rm",
            ".vob",
            ".wmv",
            ".flv",
            ".3gp",
            ".3g2",
            ".swf",
            ".mswmm",
        ]
        file_exist = False
        for i in product(exts, sys.argv):
            if i[1].endswith(i[0]) and str(i[1])[i[1].rfind("\\") :].startswith("\\"):
                path = i[1]
                directory = path[: path.rfind("\\")]
                name = path[path.rfind("\\") + 1 :].rsplit(".", 1)[0]
                ext = f".{name.rsplit('.', 1)[-1]}"
                file_exist = True
                break

        if file_exist:
            setattr(VideoFile, "name", name)
            setattr(VideoFile, "ext", ext)
            setattr(VideoFile, "path", path)
            setattr(VideoFile, "directory", directory)
        else:
            setattr(VideoFile, "path", None)
            setattr(VideoFile, "ext", None)
            setattr(VideoFile, "name", None)
            setattr(VideoFile, "directory", None)
