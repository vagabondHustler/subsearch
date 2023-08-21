import tkinter as tk

from subsearch.data import __version__
from subsearch.data.constants import APP_PATHS, FILE_PATHS
from subsearch.gui.resources import config as cfg
from subsearch.utils import io_toml, io_winreg


class WindowPosition(tk.Frame):
    def __init__(self, parent) -> None:
        tk.Frame.__init__(self, parent)

    def set(self, **kwargs):
        w = kwargs.get("w", cfg.size.width)
        h = kwargs.get("h", cfg.size.height)
        ws_value_offset = kwargs.get("ws_value_offset", 0)
        hs_value_offset = kwargs.get("hs_value_offset", 0)
        ws = self.winfo_screenwidth() + ws_value_offset
        hs = self.winfo_screenheight() + hs_value_offset
        x = int((ws / 2) - (w / 2))
        y = int((hs / 2) - (h / 2))
        value = f"{w}x{h}+{x}+{y}"
        return value


class ToolTip(tk.Toplevel):
    def __init__(self, parent, widget, *text_strings, **kwargs):
        self.parent = parent
        self.widget = widget
        self.text = text_strings
        self.background = kwargs.get("bg", cfg.color.light_black)

    def show(self) -> None:
        tk.Toplevel.__init__(self, self.parent)
        self.configure(background=self.background)
        # remove the standard window titlebar from the tooltip
        self.overrideredirect(True)
        # unpack *args and put each /n on a new line
        lines = "\n".join(self.text)
        frame = tk.Frame(self, background=self.background)
        label = tk.Label(
            frame,
            text=lines,
            background=self.background,
            foreground=cfg.color.default_fg,
            justify="left",
        )
        # get size of the label to use later for positioning and sizing of the tooltip
        x, y = label.winfo_reqwidth(), label.winfo_reqheight()
        # set the size of the tooltip background to be 1px larger than the label
        frame.configure(width=x + 1, height=y + 1)

        widget_posx = self.widget.winfo_rootx()
        widget_width = self.widget.winfo_reqwidth()
        widget_center = round(widget_width / 2)
        btn_pos_middle = widget_posx + widget_center
        frame_width = frame.winfo_reqwidth()
        frame_center = round(frame_width / 2)
        center_tip_over_mouse = btn_pos_middle - frame_center
        # offset the frame 1px from edge of the tooltip corner
        frame.place(x=1, y=1, anchor="nw")
        label.place(x=0, y=0, anchor="nw")
        root_x = center_tip_over_mouse  # offset the tooltip by extra 4px so it doesn't overlap the widget
        root_y = self.widget.winfo_rooty() - self.widget.winfo_height() - 4
        # set position of the tooltip, size and add 2px around the tooltip for a 1px border
        self.geometry(f"{x+2}x{y+2}+{root_x}+{root_y}")

    def hide(self) -> None:
        self.destroy()


def configure_root(root):
    if io_toml.load_toml_value(FILE_PATHS.config, "gui.context_menu"):
        io_winreg.add_context_menu()
    root.configure(background=cfg.color.default_bg)
    root.iconbitmap(APP_PATHS.gui_assets / "subsearch.ico")
    root.geometry(WindowPosition.set(root))  # type: ignore
    root.resizable(False, False)
