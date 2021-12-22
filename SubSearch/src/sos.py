import os

# current working directory path
def cwd():
    return os.getcwd()


# get file path inside root directory
def root_directory_file(file_name: str) -> str:
    root_dir_path, _file_name = os.path.split(os.path.abspath(__file__))
    root_dir_path = root_dir_path.replace(r"\src", "")
    file_path = f"{root_dir_path}\\{file_name}"
    return file_path


# get root directory path
def root_directory() -> str:
    root_dir_path, _file_name = os.path.split(os.path.abspath(__file__))
    root_dir_path = root_dir_path.replace(r"\src", "")
    return root_dir_path
