import sys
from itertools import product
from pathlib import Path
from typing import no_type_check

from subsearch.data.data_objects import AppPaths, FileData


def paths() -> AppPaths:
    """
    Returns an instance of the AppPaths class representing the path configuration for Subsearch application.

    Returns:
        AppPaths: An instance of AppPaths representing the path configuration for Subsearch application.
    """
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
    Returns an instance of the FileData class based on the file path provided in the command line arguments.

    The function receives no inputs.

    Returns:
      An instance of the FileData class containing the video file data. None if the file path is not valid or not one of the supported extensions (.avi, .mp4, .mkv, .mpg, .mpeg, .mov, .rm, .vob, .wmv, .flv, .3gp, .3g2, .swf, .mswmm)

    FileData class:
      name (str): the name of the video file without the extension
      extension (str): the extension of the video file (e.g. ".avi")
      file_path (Path): the absolute path to the video file
      directory (Path): the parent directory of the video file
      subs_directory (Path): the absolute path to a directory to save the subtitles (same as the parent directory for the video file)
      tmp_directory (Path): the absolute path to the local temporary files directory (".subsearch" folder within the parent directory of the video file)
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


video_data = video_file()
app_paths = paths()
