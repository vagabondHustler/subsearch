import os
import shutil

path_src = f"{os.getcwd()}/SubSearch"
zip_dst = f"{os.getcwd()}/SubSearch.zip"


def make_archive(source, destination):
    base = os.path.basename(destination)
    name = base.split(".")[0]
    format = base.split(".")[1]
    archive_from = os.path.dirname(source)
    archive_to = os.path.basename(source.strip(os.sep))
    shutil.make_archive(name, format, archive_from, archive_to)
    shutil.move("%s.%s" % (name, format), destination)


make_archive(path_src, zip_dst)
