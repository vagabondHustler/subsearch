import shutil
from pathlib import Path

"""
Used by release.yml in .github/workflows to create a zip files of the repository contents
"""


path_x64_dir_src = Path(Path.cwd()) / "subsearch-x64" / "subsearch"
path_x64_zip_dst = Path(Path.cwd()) / "subsearch-x64.zip"


def make_archive(source: str, destination: str):
    """
    Adds folder and file contents to a zip file

    Args:
        source (str): Source folder and file contents to be added into a zip file
        destination (str): Destination of the zip file
    """
    base = Path(destination)
    name = base.stem
    format = base.suffix[1:]
    archive_from = Path(source).parent
    archive_to = Path(source).name
    shutil.make_archive(name, format, archive_from, archive_to)
    shutil.move("%s.%s" % (name, format), destination)


make_archive(path_x64_dir_src, path_x64_zip_dst)
