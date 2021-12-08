from src.tools.os import root_directory_file
from src.tools.data import read_data


def get(output):
    config_json = read_data(root_directory_file("config.json"))

    def language() -> str:
        with open(root_directory_file(config_json.language), "r", encoding="utf-8") as f:
            line = f.readline()
            return line

    def languages() -> list:
        lines: list = []
        with open(root_directory_file(config_json.user_config), "r", encoding="utf-8") as f:
            _lines = f.readlines()
            for line in _lines:
                _line = line.strip()
                lines.append(_line)
            return lines

    if output == "language":
        return language()
    if output == "languages":
        return languages()
