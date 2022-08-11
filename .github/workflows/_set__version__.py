import json
import os

cwd = os.getcwd()


def read_data(config_file: str):
    with open(config_file, encoding="utf-8") as file:
        data = json.load(file)
        version = data["version"]
        return version


def current():
    c_version = read_data(f"{cwd}/src/subsearch/data/version.json")
    return c_version


v = current().replace("v", "")
version = f"""__version__ = "{v}"
"""

with open(f"{cwd}/src/subsearch/data/__version__.py", "w") as file:
    file.write(str(version))
