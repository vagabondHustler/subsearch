import sys
from itertools import product
from pathlib import Path

from subsearch.data.data_fields import VideoFileData


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
            file_path = Path(i[1])
            directory = file_path.parent
            tmp_directory = Path(directory) / ".subsearch"
            subs_directory = Path(directory) / "subs"
            name = file_path.stem
            ext = file_path.suffix
            file_exist = True
            break

    if file_exist:
        return VideoFileData(name, ext, file_path, directory, subs_directory, tmp_directory)


__video__ = get_video_file_data()
