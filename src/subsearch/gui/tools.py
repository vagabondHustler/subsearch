import ctypes
import os
import tkinter as tk
from tkinter import Label, StringVar

from subsearch.data import __buttons__
from subsearch.gui import tkdata

TKCOLOR = tkdata.Color()
TKFONT = tkdata.Font()
TKWINDOW = tkdata.Window()

GWL_EXSTYLE = -20
WS_EX_APPWINDOW = 0x00040000
WS_EX_TOOLWINDOW = 0x00000080


def buttons(btn: str):
    return os.path.join(__buttons__, btn)


# create custom labels and buttons in grid
class Create(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TKCOLOR.dark_grey)

    # create a basic label
    def label(
        self,
        bg=TKCOLOR.dark_grey,
        fg=TKCOLOR.white_grey,
        text=None,
        textvar=None,
        row=1,
        col=1,
        anchor=None,
        sticky=None,
        font=TKFONT.cas8b,
        padx=2,
        pady=2,
    ):
        _label = tk.Label(self, text=text, textvariable=textvar, font=font, fg=fg, anchor=anchor)
        _label.configure(bg=bg, fg=fg, font=font)
        _label.grid(row=row, column=col, sticky=sticky, padx=padx, pady=pady)
        return _label

    # create a basic button
    def button(
        self,
        widget_refrence=None,
        bg=TKCOLOR.light_black,
        abgc=TKCOLOR.orange,
        bge=TKCOLOR.black,
        fg=TKCOLOR.white_grey,
        fge=TKCOLOR.orange,
        text=None,
        height=2,
        width=10,
        bd=0,
        row=1,
        col=3,
        sticky=None,
        font=TKFONT.cas8b,
        padx=5,
        pady=2,
        bind_to=None,
        tip_show=False,
        tip_text="",
    ):
        _button = tk.Button(self, text=text, height=height, width=width, bd=bd)
        _button.configure(activebackground=abgc, bg=bg, fg=fg, font=font)
        _button.grid(row=row, column=col, padx=padx, pady=pady, sticky=sticky)
        _button.bind("<Button-1>", bind_to)
        tip = ToolTip(_button, _button, tip_text) if tip_show else None

        def button_enter(self):
            _button.configure(bg=bge, fg=fge, font=font)
            tip.show() if tip_show else None

        def button_leave(self):
            _button.configure(bg=bg, fg=fg, font=font)
            tip.hide() if tip is not None else None

        _button.bind("<Enter>", button_enter)
        _button.bind("<Leave>", button_leave)
        return _button


# replace the regular windows-style title bar with a custom one
class CustomTitleBar(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self._offsetx = 0
        self._offsety = 0
        self.parent = parent
        self.after(10, self.remove_old_tb(), self.parent)
        self.parent.focus_force()
        self.parent.overrideredirect(True)
        # place new bar at top of window
        self.bar = tk.Frame(height=37, width=TKWINDOW.width, bg=TKCOLOR.light_black)
        self.bar.place(x=0, y=0)
        # place SubSearch in bar
        self.subsearch_label = tk.Label(
            self.bar,
            text="SubSearch",
            bg=TKCOLOR.light_black,
            fg=TKCOLOR.white_grey,
            font=TKFONT.cas10b,
            justify="center",
            anchor="w",
        )
        self.subsearch_label.place(bordermode="inside", relx=0, y=18, anchor="w")
        # png paths
        self.exit_path = buttons("exit.png")
        self.tab_path = buttons("tab.png")
        self.exit_grey_path = buttons("exit_grey.png")
        self.tab_grey_path = buttons("tab_grey.png")
        self.max_ina_path = buttons("maximize_inactive.png")
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
        self.subsearch_label.bind("<Button-1>", self.tb_press)
        self.subsearch_label.bind("<B1-Motion>", self.tb_drag)
        # bind titlebar for dragging around window
        self.bar.bind("<Button-1>", self.tb_press)
        self.bar.bind("<B1-Motion>", self.tb_drag)
        # bind exit to close window and update png
        self.exit.bind("<Enter>", self.exit_enter)
        self.exit.bind("<Leave>", self.exit_leave)
        # bind tab to tab window and update png
        self.tab.bind("<Enter>", self.tab_enter)
        self.tab.bind("<Leave>", self.tab_leave)
        self.parent.bind("<Enter>", self.parent_enter)
        self.parent.bind("<Leave>", self.parent_leave)

        # hide 1px Frame
        self.place(relx=1, rely=1, anchor="n")
        self.configure(bg=TKCOLOR.green)

    def window_pos(self, parent, w: int = 80, h: int = 48):
        ws = parent.winfo_screenwidth()
        hs = parent.winfo_screenheight()

        x = int((ws / 2) - (w / 2))
        y = int((hs / 2) - (h / 2))
        value = f"{w}x{h}+{x}+{y}"
        return value

    def remove_old_tb(self):
        hwnd = ctypes.windll.user32.GetParent(self.parent.winfo_id())
        style = ctypes.windll.user32.GetWindowLongPtrW(hwnd, GWL_EXSTYLE)
        style = style & ~WS_EX_TOOLWINDOW
        style = style | WS_EX_APPWINDOW
        res = ctypes.windll.user32.SetWindowLongPtrW(hwnd, GWL_EXSTYLE, style)
        self.parent.withdraw()
        self.parent.after(100, lambda: self.parent.wm_deiconify())

    def tb_press(self, event):
        self._offsetx = self.parent.winfo_pointerx() - self.parent.winfo_rootx()
        self._offsety = self.parent.winfo_pointery() - self.parent.winfo_rooty()

    def tb_drag(self, event):
        x = self.winfo_pointerx() - self._offsetx
        y = self.winfo_pointery() - self._offsety
        self.parent.geometry(f"+{x}+{y}")

    def check_window_state(self, event):
        if event.widget == self.parent:
            if self.parent.state() == "iconic":
                pass
            if self.parent.state() == "normal":
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

    def exit_release(self, event):
        self.parent.destroy()

    def exit_press(self, event):
        self.exit.configure(bg=TKCOLOR.dark_red)
        self.exit.bind("<ButtonRelease-1>", self.exit_release)

    def exit_enter(self, event):
        self.exit.configure(bg=TKCOLOR.red)
        self.update_img(self.exit, self.exit_png)
        self.exit.bind("<ButtonPress-1>", self.exit_press)

    def exit_leave(self, event):
        self.exit.configure(bg=TKCOLOR.light_black)
        self.update_img(self.exit, self.exit_grey_png)
        self.exit.unbind("<ButtonRelease-1>")

    def tab_press(self, event):
        self.tab.configure(bg=TKCOLOR.light_grey)
        self.tab.bind("<ButtonRelease-1>", self.tabbing)

    def tab_enter(self, event):
        self.tab.configure(bg=TKCOLOR.dark_grey)
        self.update_img(self.tab, self.tab_png)
        self.tab.bind("<ButtonPress-1>", self.tab_press)

    def tab_leave(self, event):
        self.tab.configure(bg=TKCOLOR.light_black)
        self.update_img(self.tab, self.tab_grey_png)
        self.tab.unbind("<ButtonRelease-1>")

    def parent_enter(self, event):
        self.parent.attributes("-topmost", False)

    def parent_leave(self, evnt):
        self.parent.attributes("-topmost", True)

    def update_img(self, canvas, img):
        canvas.delete("all")
        canvas.create_image(18, 18, image=img)
        canvas.photoimage = img


# create a custom border for window
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


# get the window position so it can be placed in the center of the screen
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


# pick a appropriate color for StringVar based on the string
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
        # offset the frame 1px from edge of the tooltip corner
        frame.place(x=1, y=1, anchor="nw")
        label.place(x=0, y=0, anchor="nw")
        root_x = (
            self.widget.winfo_rootx() + self.widget.winfo_width() + 4
        )  # offset the tooltip by extra 4px so it doesn't overlap the widget
        root_y = self.widget.winfo_rooty() - self.widget.winfo_height() - 4
        # set position of the tooltip, size and add 2px around the tooltip for a 1px border
        self.geometry(f"{x+2}x{y+2}+{root_x}+{root_y}")

    def hide(self):
        self.destroy()
