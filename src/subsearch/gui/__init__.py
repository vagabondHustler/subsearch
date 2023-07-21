import re
from tkinter import Tk

from subsearch.data.constants import APP_PATHS


def get_sprites() -> dict:
    pattern = r"\b(\w+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\b"
    data = {}
    file_path = APP_PATHS.gui_styles / "sprites.tcl"
    with file_path.open() as file:
        content = file.read()
        matches = re.findall(pattern, content)

        for match in matches:
            key = match[0]
            values = tuple(map(int, match[1:]))
            data[key] = values

    return data


root = Tk(className="Subsearch")
sprites = get_sprites()
