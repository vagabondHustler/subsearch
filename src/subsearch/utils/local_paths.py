import os


# current working directory path
def cwd() -> str:
    return os.getcwd()


# get root directory path
def _paths(file_name: str = None) -> dict:
    _path, _i = os.path.split(os.path.abspath(__file__))
    if file_name is None:
        file = ""
    else:
        file = f"\\{file_name}"
    _dict = {
        "cwd": cwd(),
        "root": _path.replace("\\utils", f"{file}"),
        "data": _path.replace("\\utils", f"\\data{file}"),
        "gui": _path.replace("\\utils", f"\\gui{file}"),
        "scraper": _path.replace("\\utils", f"\\scraper{file}"),
        "utils": f"{_path}{file}",
        "icons": _path.replace("\\utils", f"\\assets\\icons{file}"),
        "buttons": _path.replace("\\utils", f"\\assets\\buttons{file}"),
    }
    return _dict


def get_path(directory: str, file_name: str = None) -> str:
    """
    get path to a directory or directory and file

    Returns
    -------
    str
        the directory or directory and file
    """
    return _paths(file_name)[f"{directory}"].lower()
