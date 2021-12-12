import os


def cwd():  # current working directory
    return os.getcwd()


def root_directory_file(file_name: str) -> str:  # file in root directory of subscene-search
    root_dir_path, _file_name = os.path.split(os.path.abspath(__file__))
    root_dir_path = root_dir_path.replace(r"\src", "")
    file_path = f"{root_dir_path}\\{file_name}"
    return file_path


def root_directory() -> str:  # root directory of subscene-search
    root_dir_path, _file_name = os.path.split(os.path.abspath(__file__))
    root_dir_path = root_dir_path.replace(r"\src", "")
    file_path = f"{root_dir_path}"
    return file_path


