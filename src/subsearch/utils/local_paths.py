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
        "root": path.replace("\\utils", f"{file}"),
        "data": path.replace("\\utils", f"\\data{file}"),
        "gui": path.replace("\\utils", f"\\gui{file}"),
        "scraper": path.replace("\\utils", f"\\scraper{file}"),
        "utils": f"{path}{file}",
        "icons": path.replace("\\utils", f"\\assets\\icons{file}"),
        "buttons": path.replace("\\utils", f"\\assets\\buttons{file}"),
    }
    return paths


def get_path(directory: str, file_name: str = None) -> str:
    """
    get path to a directory or directory and file

    Returns
    -------
    str
        the directory or directory and file
    """
    return paths(file_name)[f"{directory}"].lower()
