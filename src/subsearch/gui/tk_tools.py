import ctypes
import os
import tkinter as tk
from tkinter import Label, StringVar

from subsearch.data import __buttons__, __tabs__, __version__
from subsearch.gui import tk_data
from subsearch.utils import raw_config

TKCOLOR = tk_data.Color()
TKFONT = tk_data.Font()
TKWINDOW = tk_data.Window()

GWL_EXSTYLE = -20
WS_EX_APPWINDOW = 0x00040000
WS_EX_TOOLWINDOW = 0x00000080


def get_btn_png(btn: str):
    return os.path.join(__buttons__, btn)


def get_tabs_png(tab: str):
    return os.path.join(__tabs__, tab)


def calculate_btn_size(_widget, _width=18, _height=2):
    generic_btn = tk.Button(_widget, width=_width, height=_height)
    x, y = generic_btn.winfo_reqwidth(), generic_btn.winfo_reqheight()
    return x, y


def set_default_grid_size(_widget, _width=18):
    btn_size = tk.Button(_widget, width=_width, height=2)
    x, y = btn_size.winfo_reqwidth(), btn_size.winfo_reqheight()
    col_count, row_count = _widget.grid_size()
    for col in range(col_count):
        _widget.grid_columnconfigure(col, minsize=x)

    for row in range(row_count):
        _widget.grid_rowconfigure(row, minsize=0)


class TitleBar(tk.Frame):
    def __init__(self, parent, root):
        tk.Frame.__init__(self, parent)
        self.configure(height=37, width=TKWINDOW.width, bg=TKCOLOR.light_black)

        self.root = root
        self.parent = parent

        self.exit_path = get_btn_png("exit.png")
        self.tab_path = get_btn_png("tab.png")

        self.exit_grey_path = get_btn_png("exit_grey.png")
        self.tab_grey_path = get_btn_png("tab_grey.png")
        self.maximize_path = get_btn_png("maximize_inactive.png")

        self.tab_png = tk.PhotoImage(file=self.tab_path)
        self.tab_grey_png = tk.PhotoImage(file=self.tab_grey_path)
        self.exit_png = tk.PhotoImage(file=self.exit_path)
        self.exit_grey_png = tk.PhotoImage(file=self.exit_grey_path)
        self.maximize_png = tk.PhotoImage(file=self.maximize_path)

        self.subsearch_label = tk.Label(
            self,
            text=f"Subsearch - v{__version__}",
            bg=TKCOLOR.light_black,
            fg=TKCOLOR.white_grey,
            font=TKFONT.cas10b,
            justify="center",
            anchor="w",
        )
        self.tab = tk.Canvas(
            self,
            width=37,
            height=37,
            bg=TKCOLOR.light_black,
            highlightthickness=0,
        )
        self.maximize = tk.Canvas(
            self,
            width=37,
            height=37,
            bg=TKCOLOR.light_black,
            highlightthickness=0,
        )
        self.exit = tk.Canvas(
            self,
            width=37,
            height=37,
            bg=TKCOLOR.light_black,
            highlightthickness=0,
        )
        self.subsearch_label.place(bordermode="inside", relx=0, y=18, anchor="w")
        self.maximize.place(x=TKWINDOW.width - 37, rely=0, anchor="ne")
        self.exit.place(relx=1, rely=0, anchor="ne")
        self.tab.place(x=TKWINDOW.width - 74, rely=0, anchor="ne")

        self.update_img(self.tab, self.tab_grey_png)
        self.update_img(self.maximize, self.maximize_png)
        self.update_img(self.exit, self.exit_grey_png)

        self.subsearch_label.bind("<Button-1>", self.press_titlebar)
        self.subsearch_label.bind("<B1-Motion>", self.drag_titlebar)

        self.bind("<Button-1>", self.press_titlebar)
        self.bind("<B1-Motion>", self.drag_titlebar)

        self.tab.bind("<Enter>", self.enter_event)
        self.exit.bind("<Enter>", self.enter_event)

        self.tab.bind("<Leave>", self.leave_event)
        self.exit.bind("<Leave>", self.leave_event)

    def update_img(self, canvas, img):
        canvas.delete("all")
        canvas.create_image(18, 18, image=img)
        canvas.photoimage = img

    def press_titlebar(self, event):
        self._offsetx = self.winfo_pointerx() - self.winfo_rootx()
        self._offsety = self.winfo_pointery() - self.winfo_rooty()

    def drag_titlebar(self, event):
        x = self.winfo_pointerx() - self._offsetx
        y = self.winfo_pointery() - self._offsety
        self.parent.geometry(f"+{x}+{y}")

    def release_event(self, event):
        if event.widget == self.tab:
            self.parent.wm_withdraw()
            self.root.wm_state("iconic")
        if event.widget == self.exit:
            self.root.destroy()

    def press_event(self, event):
        if event.widget == self.tab:
            self.tab.configure(bg=TKCOLOR.light_grey)
            self.tab.bind("<ButtonRelease-1>", self.release_event)
        if event.widget == self.exit:
            self.exit.configure(bg=TKCOLOR.dark_red)
            self.exit.bind("<ButtonRelease-1>", self.release_event)

    def enter_event(self, event):
        if event.widget == self.tab:
            self.tab.configure(bg=TKCOLOR.dark_grey)
            self.update_img(self.tab, self.tab_png)
            self.tab.bind("<ButtonPress-1>", self.press_event)
        if event.widget == self.exit:
            self.exit.configure(bg=TKCOLOR.red)
            self.update_img(self.exit, self.exit_png)
            self.exit.bind("<ButtonPress-1>", self.press_event)

    def leave_event(self, event):
        if event.widget == self.tab:
            self.tab.configure(bg=TKCOLOR.light_black)
            self.update_img(self.tab, self.tab_grey_png)
            self.tab.unbind("<ButtonRelease-1>")
        if event.widget == self.exit:
            self.exit.configure(bg=TKCOLOR.light_black)
            self.update_img(self.exit, self.exit_grey_png)
            self.exit.unbind("<ButtonRelease-1>")


class CustomBorder(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        csx = TKWINDOW.width
        csy = TKWINDOW.height
        self.canvas_border = tk.Canvas(parent, width=csx, height=csy, bg=TKCOLOR.light_black, borderwidth=0)
        self.canvas_border.place(relx=0.5, rely=0.5, anchor="center")
        self.canvas_bg = tk.Canvas(
            parent,
            width=csx - 4,
            height=csy - 4,
            bg=TKCOLOR.dark_grey,
            highlightthickness=0,
        )
        self.canvas_bg.place(relx=0.5, rely=0.5, anchor="center")

        self.configure(bg=TKCOLOR.light_black)


class WindowPosition(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

    def set(self, w=TKWINDOW.width, h=TKWINDOW.height, ws_value_offset=0, hs_value_offset=0, other: bool = False):
        ws = self.winfo_screenwidth() + ws_value_offset
        hs = self.winfo_screenheight() + hs_value_offset
        x = int((ws / 2) - (w / 2))
        y = int((hs / 2) - (h / 2))
        value = f"{w}x{h}+{x}+{y}"
        if other:
            return w, h, x, y
        return value


class ColorPicker:
    def __init__(self, string_var: StringVar, clabel: Label, is_pct: bool = False):
        self.string_var = string_var
        self.clabel = clabel
        self.is_pct = is_pct
        self.pick()

    def pick(self):  # string boolean
        if self.string_var.get() == "True":
            self.clabel.configure(fg=TKCOLOR.green)
        elif self.string_var.get() == "False":
            self.clabel.configure(fg=TKCOLOR.red)
        elif self.string_var.get() == "Both":
            self.clabel.configure(fg=TKCOLOR.blue)
        elif self.string_var.get().startswith("Only"):
            self.clabel.configure(fg=TKCOLOR.green)

        if self.is_pct:
            _pct = raw_config.get_config_key("percentage")
            if _pct in range(75, 101):
                self.clabel.configure(fg=TKCOLOR.green)
            elif _pct in range(50, 75):
                self.clabel.configure(fg=TKCOLOR.green_brown)
            elif _pct in range(25, 50):
                self.clabel.configure(fg=TKCOLOR.red_brown)
            elif _pct in range(0, 25):
                self.clabel.configure(fg=TKCOLOR.red)


class ToolTip(tk.Toplevel):
    def __init__(self, parent, widget, *text):
        self.parent = parent
        self.widget = widget
        self.text = text

    def show(self):
        tk.Toplevel.__init__(self, self.parent)
        self.configure(background=TKCOLOR.light_black)
        # remove the standard window titlebar from the tooltip
        self.overrideredirect(True)
        # unpack *args and put each /n on a new line
        lines = "\n".join(self.text)
        frame = tk.Frame(self, background=TKCOLOR.light_black)
        label = tk.Label(
            frame,
            text=lines,
            background=TKCOLOR.dark_grey,
            foreground=TKCOLOR.white_grey,
            justify="left",
        )
        # get size of the label to use later for positioning and sizing of the tooltip
        x, y = label.winfo_reqwidth(), label.winfo_reqheight()
        # set the size of the tooltip background to be 1px larger than the label
        frame.configure(width=x + 1, height=y + 1)

        widget_pos = self.widget.winfo_rootx()
        widget_width = self.widget.winfo_reqwidth()
        widget_center = round(widget_width / 2)
        btn_pos_middle = widget_pos + widget_center
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

    def hide(self):
        self.destroy()
