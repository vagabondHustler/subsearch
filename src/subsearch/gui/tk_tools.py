import tkinter as tk
from pathlib import Path
from tkinter import Label, StringVar, ttk

from subsearch.data import __icon__, __tabs__, __titlebar__, __version__, __video__
from subsearch.data.data_fields import TkColor, TkWindowSize
from subsearch.utils import raw_config

GWL_EXSTYLE = -20
WS_EX_APPWINDOW = 0x00040000
WS_EX_TOOLWINDOW = 0x00000080


def get_titlebar_png(btn: str):
    return Path(__titlebar__) / btn


def get_tab_png(tab: str):
    return Path(__tabs__) / tab


def calculate_btn_size(cls, _width=18, _height=2):
    generic_btn = tk.Button(cls, width=_width, height=_height)
    x, y = generic_btn.winfo_reqwidth(), generic_btn.winfo_reqheight()
    return x, y


def calculate_checkbtn_size(cls, _width=16):
    generic_checkbtn = ttk.Checkbutton(cls, width=_width)
    return generic_checkbtn.winfo_reqwidth()


def set_default_grid_size(cls, _width=18):
    btn_size = tk.Button(cls, width=_width, height=2)
    x, y = btn_size.winfo_reqwidth(), btn_size.winfo_reqheight()
    col_count, row_count = cls.grid_size()
    for col in range(col_count):
        cls.grid_columnconfigure(col, minsize=x)

    for row in range(row_count):
        cls.grid_rowconfigure(row, minsize=0)


def asset_tab(cls, img, type, x=27, y=27):
    path = get_tab_png(f"{img}_{type}.png")
    png = tk.PhotoImage(file=path)
    update_asset(cls, png, x, y)


def asset_titlebar(_widget, img, type, x=18, y=18):
    path = get_titlebar_png(f"{img}_{type}.png")
    png = tk.PhotoImage(file=path)
    update_asset(_widget, png, x, y)


def asset_icon(cls, x=18, y=18):
    path = str(__icon__).replace(".ico", ".png")
    ico = tk.PhotoImage(file=path)
    update_asset(cls, ico, x, y)


def update_asset(cls, img, x, y):
    cls.delete("all")
    cls.create_image(x, y, image=img)
    cls.photoimage = img


class TitleBar(tk.Frame):
    def __init__(self, parent, root):
        tk.Frame.__init__(self, parent)
        self.configure(height=37, width=TkWindowSize().width, bg=TkColor().light_black)

        self.root = root
        self.parent = parent
        self.icon = tk.Canvas(
            self,
            width=37,
            height=37,
            bg=TkColor().light_black,
            highlightthickness=0,
        )
        self.tab = tk.Canvas(
            self,
            width=37,
            height=37,
            bg=TkColor().light_black,
            highlightthickness=0,
        )
        self.maximize = tk.Canvas(
            self,
            width=37,
            height=37,
            bg=TkColor().light_black,
            highlightthickness=0,
        )
        self.exit = tk.Canvas(
            self,
            width=37,
            height=37,
            bg=TkColor().light_black,
            highlightthickness=0,
        )

        self.maximize.place(x=TkWindowSize().width - 37, rely=0, anchor="ne")
        self.exit.place(relx=1, rely=0, anchor="ne")
        self.tab.place(x=TkWindowSize().width - 74, rely=0, anchor="ne")
        self.icon.place(x=0, y=0, anchor="nw")

        asset_icon(self.icon)
        asset_titlebar(self.tab, "tab", "rest")
        asset_titlebar(self.maximize, "maximize", "disabled")
        asset_titlebar(self.exit, "exit", "rest")

        self.icon.bind("<Button-1>", self.press_titlebar)
        self.icon.bind("<B1-Motion>", self.drag_titlebar)

        self.bind("<Button-1>", self.press_titlebar)
        self.bind("<B1-Motion>", self.drag_titlebar)

        self.tab.bind("<Enter>", self.enter_event)
        self.exit.bind("<Enter>", self.enter_event)

        self.tab.bind("<Leave>", self.leave_event)
        self.exit.bind("<Leave>", self.leave_event)

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
            self.tab.configure(bg=TkColor().light_grey)
            self.tab.bind("<ButtonRelease-1>", self.release_event)
        if event.widget == self.exit:
            self.exit.configure(bg=TkColor().dark_red)
            self.exit.bind("<ButtonRelease-1>", self.release_event)

    def enter_event(self, event):
        if event.widget == self.tab:
            self.tab.configure(bg=TkColor().dark_grey)
            asset_titlebar(self.tab, "tab", "hover")
            self.tab.bind("<ButtonPress-1>", self.press_event)
        if event.widget == self.exit:
            self.exit.configure(bg=TkColor().red)
            asset_titlebar(self.exit, "exit", "hover")
            self.exit.bind("<ButtonPress-1>", self.press_event)

    def leave_event(self, event):
        if event.widget == self.tab:
            self.tab.configure(bg=TkColor().light_black)
            asset_titlebar(self.tab, "tab", "rest")
            self.tab.unbind("<ButtonRelease-1>")
        if event.widget == self.exit:
            self.exit.configure(bg=TkColor().light_black)
            asset_titlebar(self.exit, "exit", "rest")
            self.exit.unbind("<ButtonRelease-1>")


class CustomBorder(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        csx = TkWindowSize().width
        csy = TkWindowSize().height
        self.canvas_border = tk.Canvas(parent, width=csx, height=csy, bg=TkColor().light_black, borderwidth=0)
        self.canvas_border.place(relx=0.5, rely=0.5, anchor="center")
        self.canvas_bg = tk.Canvas(
            parent,
            width=csx - 4,
            height=csy - 4,
            bg=TkColor().dark_grey,
            highlightthickness=0,
        )
        self.canvas_bg.place(relx=0.5, rely=0.5, anchor="center")

        self.configure(bg=TkColor().light_black)


class WindowPosition(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

    def set(
        self, w=TkWindowSize().width, h=TkWindowSize().height, ws_value_offset=0, hs_value_offset=0, other: bool = False
    ):
        ws = self.winfo_screenwidth() + ws_value_offset
        hs = self.winfo_screenheight() + hs_value_offset
        x = int((ws / 2) - (w / 2))
        y = int((hs / 2) - (h / 2))
        value = f"{w}x{h}+{x}+{y}"
        if other:
            return w, h, x, y
        return value


class VarColorPicker:
    def __init__(self, string_var: StringVar, clabel: Label, is_pct: bool = False):
        self.string_var = string_var
        self.clabel = clabel
        self.is_pct = is_pct
        self.pick()

    def pick(self):  # string boolean
        if self.string_var.get() == "True":
            self.clabel.configure(fg=TkColor().green)
        elif self.string_var.get() == "False":
            self.clabel.configure(fg=TkColor().red)
        elif self.string_var.get() == "Both":
            self.clabel.configure(fg=TkColor().blue)
        elif self.string_var.get().startswith("Only"):
            self.clabel.configure(fg=TkColor().green)

        if self.is_pct:
            _pct = raw_config.get_config_key("percentage")
            if _pct in range(75, 101):
                self.clabel.configure(fg=TkColor().green)
            elif _pct in range(50, 75):
                self.clabel.configure(fg=TkColor().green_brown)
            elif _pct in range(25, 50):
                self.clabel.configure(fg=TkColor().red_brown)
            elif _pct in range(0, 25):
                self.clabel.configure(fg=TkColor().red)


class ToolTip(tk.Toplevel):
    def __init__(self, parent, _widget, *_text, _background=TkColor().light_black):
        self.parent = parent
        self.widget = _widget
        self.text = _text
        self.background = _background

    def show(self):
        tk.Toplevel.__init__(self, self.parent)
        self.configure(background=TkColor().light_black)
        # remove the standard window titlebar from the tooltip
        self.overrideredirect(True)
        # unpack *args and put each /n on a new line
        lines = "\n".join(self.text)
        frame = tk.Frame(self, background=TkColor().light_black)
        label = tk.Label(
            frame,
            text=lines,
            background=self.background,
            foreground=TkColor().white_grey,
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
