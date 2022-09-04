import sys
from dataclasses import dataclass
from itertools import product


@dataclass(order=True)
class VideoFileData:
    name: str | None
    ext: str | None
    path: str | None
    directory: str | None


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
            name = path[path.rfind("\\") + 1 :].rsplit(".", 1)[0]
            ext = i[0]
            file_exist = True
            break

    if file_exist:
        return VideoFileData(name, ext, path, directory)
    else:
        return VideoFileData(None, None, None, None)
