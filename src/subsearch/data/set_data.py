import sys
from itertools import product
from pathlib import Path
from typing import no_type_check

from subsearch.data.data_objects import AppPaths, FileData


def paths() -> AppPaths:
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


@no_type_check
def video_file() -> FileData:

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
            file_path = Path(i[1])
            directory = file_path.parent
            tmp_directory = Path(directory) / ".subsearch"
            subs_directory = Path(directory) / "subs"
            name = file_path.stem
            ext = file_path.suffix
            file_exist = True
            break

    if file_exist:
        return FileData(name, ext, file_path, directory, subs_directory, tmp_directory)


__video__ = video_file()
__paths__ = paths()
