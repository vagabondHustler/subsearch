import os


# current working directory path
def cwd():
    return os.getcwd()


# get root directory path
def root_directory(directory: str = "src", file_name: str=None):
    path, _i = os.path.split(os.path.abspath(__file__))
    if directory == "src":
        path = path.replace(r"\src\utilities", "")
    if directory == "data":
        path = path.replace(r"\src\utilities", "\src\data")
    if directory == "gui":
        path = path.replace(r"\src\utilities", "\src\gui")
    if directory == "scraper":
        path = path.replace(r"\src\utilities", "\src\scraper")
    if directory == "utilities":
        pass
    if file_name is not None:
        path = add_file_to_path(path, file_name)
    return path


def add_file_to_path(root_dir_path: str, file_name: str):
    file_path = f"{root_dir_path}\{file_name}"
    return file_path
