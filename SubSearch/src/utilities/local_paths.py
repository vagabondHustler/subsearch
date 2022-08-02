import os

# current working directory path
def cwd():
    return os.getcwd()


# get root directory path
def paths(file_name: str = None):
    path, _i = os.path.split(os.path.abspath(__file__))
    if file_name is None:
        file = ""
    else:
        file = f"\\{file_name}"
    paths = {
        "cwd": cwd(),
        "root": path.replace("\\src\\utilities", f"{file}"),
        "src": path.replace("\\src\\utilities", f"\\src{file}"),
        "data": path.replace("\\src\\utilities", f"\\src\\data{file}"),
        "gui": path.replace("\\src\\utilities", f"\\src\\gui{file}"),
        "scraper": path.replace("\\src\\utilities", f"\\src\\scraper{file}"),
        "icons": path.replace("\\src\\utilities", f"\\src\\gui\\assets\\icons{file}"),
        "buttons": path.replace("\\src\\utilities", f"\\src\\gui\\assets\\buttons{file}"),
        "utilities": path,
    }
    return paths

def get_path(directory: str, file_name: str = None):
    """get_path to a directory or directory and file

    Args:
        directory: src, data, gui, scraper, icons, buttons, utilities
        file_name: any. Defaults to None.

    Returns:
        dict[str, str]: path to directory or directory and file
    """
    return paths(file_name)[f"{directory}"].lower()

def add_file_to_path(root_dir_path: str, file_name: str):
    file_path = f"{root_dir_path}\{file_name}"
    return file_path
