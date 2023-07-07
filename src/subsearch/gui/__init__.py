import re
from tkinter import Tk

from subsearch.data import app_paths


def get_spritesheet_data() -> dict:
    pattern = r"\b(\w+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\b"
    data = {}
    file_path = app_paths.gui_app_theme / "spritesheet_data.tcl"
    with file_path.open() as file:
        content = file.read()
        matches = re.findall(pattern, content)

        for match in matches:
            key = match[0]
            values = tuple(map(int, match[1:]))
            data[key] = values

    return data


root = Tk(className="Subsearch")
spritesheet_data = get_spritesheet_data()
