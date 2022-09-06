import os
import sys
from dataclasses import dataclass
from itertools import product
from typing import Any


@dataclass(order=True)
class VideoFileData:
    name: str | Any
    ext: str | Any
    path: str | Any
    directory: str | Any
    subs_directory: str | Any
    tmp_directory: str | Any


def get_video_file_data() -> VideoFileData:

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
            tmp_directory = os.path.join(directory, ".subsearch")
            subs_directory = os.path.join(directory, "subs")
            name = path[path.rfind("\\") + 1 :].rsplit(".", 1)[0]
            ext = i[0]
            file_exist = True
            break

    if file_exist:
        return VideoFileData(name, ext, path, directory, subs_directory, tmp_directory)
    else:
        return VideoFileData(name=None, ext=None, path=None, directory=None, subs_directory=None, tmp_directory=None)
