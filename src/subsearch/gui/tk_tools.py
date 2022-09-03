import ctypes
import os
import tkinter as tk
from tkinter import Label, StringVar

from subsearch.data import __buttons__, __tabs__, __version__
from subsearch.gui import tk_data

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


class CustomTitleBar(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self._offsetx = 0
        self._offsety = 0
        self.parent = parent
        self.after(10, self.set_deiconify(), self.parent)
        self.parent.focus_force()
        self.parent.overrideredirect(True)
        # place new bar at top of window
        self.bar = tk.Frame(height=37, width=TKWINDOW.width, bg=TKCOLOR.light_black)
        self.bar.place(x=0, y=0)
        # place SubSearch in bar
        self.subsearch_label = tk.Label(
            self.bar,
            text=f"Subsearch - v{__version__}",
            bg=TKCOLOR.light_black,
            fg=TKCOLOR.white_grey,
            font=TKFONT.cas10b,
            justify="center",
            anchor="w",
        )
        self.subsearch_label.place(bordermode="inside", relx=0, y=18, anchor="w")
        # png paths
        self.exit_path = get_btn_png("exit.png")
        self.tab_path = get_btn_png("tab.png")
        self.exit_grey_path = get_btn_png("exit_grey.png")
        self.tab_grey_path = get_btn_png("tab_grey.png")
        self.max_ina_path = get_btn_png("maximize_inactive.png")
        # PhotoImages
        self.tab_png = tk.PhotoImage(file=self.tab_path)
        self.tab_grey_png = tk.PhotoImage(file=self.tab_grey_path)
        self.exit_png = tk.PhotoImage(file=self.exit_path)
        self.exit_grey_png = tk.PhotoImage(file=self.exit_grey_path)
        self.max_ina_png = tk.PhotoImage(file=self.max_ina_path)
        # place exit canvas and image
        self.exit = tk.Canvas(
            self.bar,
            width=37,
            height=37,
            bg=TKCOLOR.light_black,
            highlightthickness=0,
        )
        self.exit.place(relx=1, rely=0, anchor="ne")
        self.update_img(self.exit, self.exit_grey_png)
        # place maximize canvas and image
        self.maximize = tk.Canvas(
            self.bar,
            width=37,
            height=37,
            bg=TKCOLOR.light_black,
            highlightthickness=0,
        )
        self.maximize.place(x=TKWINDOW.width - 37, rely=0, anchor="ne")
        self.update_img(self.maximize, self.max_ina_png)
        # place tab canvas and image
        self.tab = tk.Canvas(
            self.bar,
            width=37,
            height=37,
            bg=TKCOLOR.light_black,
            highlightthickness=0,
        )
        self.tab.place(x=TKWINDOW.width - 74, rely=0, anchor="ne")
        self.update_img(self.tab, self.tab_grey_png)
        # binds
        # bind label for dragging around window
        self.subsearch_label.bind("<Button-1>", self.press_titlebar)
        self.subsearch_label.bind("<B1-Motion>", self.drag_titlebar)
        # bind titlebar for dragging around window
        self.bar.bind("<Button-1>", self.press_titlebar)
        self.bar.bind("<B1-Motion>", self.drag_titlebar)
        # bind exit to close window and update png
        self.exit.bind("<Enter>", self.enter_exit)
        self.exit.bind("<Leave>", self.leave_exit)
        # bind tab to tab window and update png
        self.tab.bind("<Enter>", self.enter_tab)
        self.tab.bind("<Leave>", self.leave_tab)
        self.parent.bind("<Enter>", self.enter_parent)
        self.parent.bind("<Leave>", self.leave_parent)

        # hide 1px Frame
        self.place(relx=1, rely=1, anchor="n")
        self.configure(bg=TKCOLOR.green)

    def get_window_pos(self, parent, w: int = 80, h: int = 48):
        ws = parent.winfo_screenwidth()
        hs = parent.winfo_screenheight()

        x = int((ws / 2) - (w / 2))
        y = int((hs / 2) - (h / 2))
        value = f"{w}x{h}+{x}+{y}"
        return value

    def set_deiconify(self):
        hwnd = ctypes.windll.user32.GetParent(self.parent.winfo_id())
        style = ctypes.windll.user32.GetWindowLongPtrW(hwnd, GWL_EXSTYLE)
        style = style & ~WS_EX_TOOLWINDOW
        style = style | WS_EX_APPWINDOW
        res = ctypes.windll.user32.SetWindowLongPtrW(hwnd, GWL_EXSTYLE, style)
        self.parent.withdraw()
        self.parent.after(100, lambda: self.parent.wm_deiconify())

    def press_titlebar(self, event):
        self._offsetx = self.parent.winfo_pointerx() - self.parent.winfo_rootx()
        self._offsety = self.parent.winfo_pointery() - self.parent.winfo_rooty()

    def drag_titlebar(self, event):
        x = self.winfo_pointerx() - self._offsetx
        y = self.winfo_pointery() - self._offsety
        self.parent.geometry(f"+{x}+{y}")

    def check_window_state(self, event):
        if event.widget == self.parent and self.parent.state() == "normal":
            self.parent.overrideredirect(True)
            self.parent.attributes("-alpha", 1)
            self.parent.deiconify()

    def tabbing(self, event):
        self.parent.attributes("-topmost", False)
        self.parent.wm_attributes("-transparentcolor", TKCOLOR.black)
        self.parent.attributes("-alpha", 0.1)
        self.parent.overrideredirect(False)
        self.parent.iconify()
        self.parent.bind("<FocusIn>", self.check_window_state)

    def release_exit(self, event):
        self.parent.destroy()

    def press_exit(self, event):
        self.exit.configure(bg=TKCOLOR.dark_red)
        self.exit.bind("<ButtonRelease-1>", self.release_exit)

    def enter_exit(self, event):
        self.exit.configure(bg=TKCOLOR.red)
        self.update_img(self.exit, self.exit_png)
        self.exit.bind("<ButtonPress-1>", self.press_exit)

    def leave_exit(self, event):
        self.exit.configure(bg=TKCOLOR.light_black)
        self.update_img(self.exit, self.exit_grey_png)
        self.exit.unbind("<ButtonRelease-1>")

    def press_tab(self, event):
        self.tab.configure(bg=TKCOLOR.light_grey)
        self.tab.bind("<ButtonRelease-1>", self.tabbing)

    def enter_tab(self, event):
        self.tab.configure(bg=TKCOLOR.dark_grey)
        self.update_img(self.tab, self.tab_png)
        self.tab.bind("<ButtonPress-1>", self.press_tab)

    def leave_tab(self, event):
        self.tab.configure(bg=TKCOLOR.light_black)
        self.update_img(self.tab, self.tab_grey_png)
        self.tab.unbind("<ButtonRelease-1>")

    def enter_parent(self, event):
        self.parent.attributes("-topmost", False)

    def leave_parent(self, evnt):
        self.parent.attributes("-topmost", True)

    def update_img(self, canvas, img):
        canvas.delete("all")
        canvas.create_image(18, 18, image=img)
        canvas.photoimage = img


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

    def set(
        self,
        w=TKWINDOW.width,
        h=TKWINDOW.height,
        ws_value_offset=0,
        hs_value_offset=0,
    ):
        ws = self.winfo_screenwidth() + ws_value_offset
        hs = self.winfo_screenheight() + hs_value_offset
        x = int((ws / 2) - (w / 2))
        y = int((hs / 2) - (h / 2))
        value = f"{w}x{h}+{x}+{y}"
        return value


class ColorPicker:
    def __init__(self, string_var: StringVar, clabel: Label, pct: int = -1):
        self.string_var = string_var
        self.clabel = clabel
        self.pct = pct
        self.pick()

    def pick(self):  # string boolean
        if self.string_var.get() == "True":
            self.clabel.configure(fg=TKCOLOR.green)
        elif self.string_var.get() == "False":
            self.clabel.configure(fg=TKCOLOR.red)
        elif self.string_var.get() == "Both":
            self.clabel.configure(fg=TKCOLOR.blue)
        # range
        elif self.pct in range(75, 100):
            self.clabel.configure(fg=TKCOLOR.green)
        elif self.pct in range(50, 75):
            self.clabel.configure(fg=TKCOLOR.green_brown)
        elif self.pct in range(25, 50):
            self.clabel.configure(fg=TKCOLOR.red_brown)
        elif self.pct in range(0, 25):
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
