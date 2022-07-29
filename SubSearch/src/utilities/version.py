import json

from src.utilities.edit_config import update_json
from src.utilities.local_paths import root_directory


def read_data(config_file: str):
    with open(config_file, encoding="utf-8") as file:
        data = json.load(file)
        version = data["version"]
        return version


def current_version():
    c_version = read_data(root_directory("data", "version.json"))
    return c_version


version_on_load = current_version()


def increase_version(current_version: str, release_type: str, i: int = 1):
    """
    Increase the version number

    :param str current_version: The current version number
    :param str release_type: (major, minor, or patch)
    :return str: _description_
    """
    c_version = current_version.replace("v", "")
    major, minor, patch = c_version.split(".")
    if release_type.lower() == "patch":
        patch = int(patch) + i
    if release_type.lower() == "minor":
        minor = int(minor) + i
    if release_type.lower() == "major":
        major = int(major) + i
    else:
        pass

    return f"v{major}.{minor}.{patch}"


def add_patch_minor_major(release_type: str):
    """
    Patch release (0.0.1 -> 0.0.2): bug fixes
    Minor release (0.1.0 -> 0.2.0): larger bug fixes or new features
    Major release (1.0.0 -> 2.0.0): stable releases

    :param str release_type: "major", "minor", "patch", defaults to sys.argv[1]
    """
    print(f"Current Version: {current_version()}")
    new_version = increase_version(current_version(), release_type)
    update_json("version", new_version, "data", "version.json")

    print(f"New Version: {new_version}, Old Version: {version_on_load}")
