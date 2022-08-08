import os
import shutil

"""
Used by publish.yml in .github\workflows to create a zip files of the repository contents
"""
ss_upper = f"{os.getcwd()}/src/SubSearch"
ss_lower = f"{os.getcwd()}/src/subsearch"

os.rename(ss_lower, ss_upper)
path_py_dir_src = f"{os.getcwd()}/src/SubSearch"
path_py_zip_dst = f"{os.getcwd()}/SubSearch-source.zip"
path_x64_dir_src = f"{os.getcwd()}/SubSearch-x64/SubSearch"
path_x64_zip_dst = f"{os.getcwd()}/SubSearch-x64.zip"
os.rename(ss_upper, ss_lower)


def make_archive(source: str, destination: str):
    """
    Adds folder and file contents to a zip file

    :param str source: Source folder and file contents to be added into a zip file
    :param str destination: Destination of the zip file
    """
    base = os.path.basename(destination)
    name = base.split(".")[0]
    format = base.split(".")[1]
    archive_from = os.path.dirname(source)
    archive_to = os.path.basename(source.strip(os.sep))
    shutil.make_archive(name, format, archive_from, archive_to)
    shutil.move("%s.%s" % (name, format), destination)


make_archive(path_x64_dir_src, path_x64_zip_dst)
make_archive(path_py_dir_src, path_py_zip_dst)
