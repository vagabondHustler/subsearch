import os

# current working directory path
def cwd() -> str:
    return os.getcwd()


# get root directory path
def paths(file_name: str = None) -> dict:
    path, _i = os.path.split(os.path.abspath(__file__))
    if file_name is None:
        file = ""
    else:
        file = f"\\{file_name}"
    paths = {
        "cwd": cwd(),
        "root": path.replace("\\util", f"{file}"),
        "data": path.replace("\\util", f"\\data{file}"),
        "gui": path.replace("\\util", f"\\gui{file}"),
        "scraper": path.replace("\\util", f"\\scraper{file}"),
        "util": path,
        "icons": path.replace("\\util", f"\\assets\\icons{file}"),
        "buttons": path.replace("\\util", f"\\assets\\buttons{file}"),
    }
    return paths


def get_path(directory: str, file_name: str = None) -> str:
    """get_path to a directory or directory and file

    Args:
        directory: src, data, gui, scraper, icons, buttons, utilities
        file_name: any. Defaults to None.

    Returns:
        dict[str, str]: path to directory or directory and file
    """
    return paths(file_name)[f"{directory}"].lower()


def add_file_to_path(root_dir_path: str, file_name: str) -> str:
    file_path = f"{root_dir_path}\{file_name}"
    return file_path
