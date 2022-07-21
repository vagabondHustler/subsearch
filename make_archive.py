import os
import shutil

path_x64_dir_src = f"{os.getcwd()}/app_release/SubSearch-x64"
path_x64_zip_dst = f"{os.getcwd()}/SubSearch-x64.zip"


def make_archive(source, destination):
    base = os.path.basename(destination)
    name = base.split(".")[0]
    format = base.split(".")[1]
    archive_from = os.path.dirname(source)
    archive_to = os.path.basename(source.strip(os.sep))
    shutil.make_archive(name, format, archive_from, archive_to)
    shutil.move("%s.%s" % (name, format), destination)


make_archive(path_x64_dir_src, path_x64_zip_dst)
