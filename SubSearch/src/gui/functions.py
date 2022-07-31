import ctypes
import tkinter as tk

from src.gui.tooltip import Hovertip
from src.gui.data import Window, Color, Font
from src.utilities.local_paths import root_directory

# create custom labels and buttons in grid
class Create(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=Color.dark_grey)

    # create a basic label
    def label(
        self,
        bg=Color.dark_grey,
        fg=Color.white_grey,
        text=None,
        textvar=None,
        row=None,
        col=None,
        anchor=None,
        sticky=None,
        font=Font.cas8b,
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
        bg=Color.light_black,
        abgc=Color.orange,
        bge=Color.black,
        fg=Color.white_grey,
        fge=Color.orange,
        text=None,
        height=2,
        width=10,
        bd=0,
        row=None,
        col=None,
        sticky=None,
        font=Font.cas8b,
        padx=5,
        pady=2,
        bind_to=None,
        tip_show=False,
        tip_text=None,
    ):
        _button = tk.Button(self, text=text, height=height, width=width, bd=bd)
        _button.configure(activebackground=abgc, bg=bg, fg=fg, font=font)
        _button.grid(row=row, column=col, padx=padx, pady=pady, sticky=sticky)
        _button.bind("<Button-1>", bind_to)
        tip = Hovertip(_button, tip_text) if tip_show else None

        def button_enter(self):
            _button.configure(bg=bge, fg=fge, font=font)
            tip.showtip() if tip_show else None

        def button_leave(self):
            _button.configure(bg=bg, fg=fg, font=font)
            tip.hidetip() if tip_show else None

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
        self.bar = tk.Frame(height=37, width=Window.width, bg=Color.light_black)
        self.bar.place(x=0, y=0)
        # place exit canvas
        self.exit = tk.Canvas(self.bar, width=37, height=37, bg=Color.light_black, highlightthickness=0)
        self.exit.place(relx=1, rely=0, anchor="ne")
        #place x in canvas
        png_path = root_directory("data", "x.png")
        x_exit = tk.PhotoImage(file=png_path)
        self.exit.create_image(18, 18, image=x_exit)
        self.exit.photoimage = x_exit
        # place SubSearch in bar
        self.subsearch_label = tk.Label(
            self.bar,
            text="SubSearch",
            bg=Color.light_black,
            fg=Color.white_grey,
            font=Font.cas10b,
            justify="center",
            anchor="w",
        )
        self.subsearch_label.place(bordermode="inside", relx=0, y=18, anchor="w")
        # binds
        self.subsearch_label.bind("<Button-1>", self.tb_press)
        self.subsearch_label.bind("<B1-Motion>", self.tb_drag)
        self.bar.bind("<Button-1>", self.tb_press)
        self.bar.bind("<B1-Motion>", self.tb_drag)
        self.exit.bind("<Enter>", self.exit_enter)
        self.exit.bind("<Leave>", self.exit_leave)
        
        # hide 1px Frame
        self.place(relx=1, rely=1, anchor="n")
        self.configure(bg=Color.green)

    def window_pos(self, parent, w: int = 80, h: int = 48):
        ws = parent.winfo_screenwidth()
        hs = parent.winfo_screenheight()

        x = int((ws / 2) - (w / 2))
        y = int((hs / 2) - (h / 2))
        value = f"{w}x{h}+{x}+{y}"
        return value

    def remove_old_tb(self):
        gwl_exstyle = -20
        ws_ex_appwindow = 0x00040000
        ws_ex_toolwindow = 0x00000080
        hwnd = ctypes.windll.user32.GetParent(self.parent.winfo_id())
        style = ctypes.windll.user32.GetWindowLongPtrW(hwnd, gwl_exstyle)
        style = style & ~ws_ex_toolwindow
        style = style | ws_ex_appwindow
        res = ctypes.windll.user32.SetWindowLongPtrW(hwnd, gwl_exstyle, style)
        self.parent.withdraw()
        self.parent.after(10, self.parent.deiconify)

    def tb_press(self, event):
        self._offsetx = self.parent.winfo_pointerx() - self.parent.winfo_rootx()
        self._offsety = self.parent.winfo_pointery() - self.parent.winfo_rooty()

    def tb_drag(self, event):
        x = self.winfo_pointerx() - self._offsetx
        y = self.winfo_pointery() - self._offsety
        self.parent.geometry(f"+{x}+{y}")

    def exit_release(self, event):
        self.parent.destroy()

    def exit_press(self, event):
        self.exit.configure(bg=Color.dark_red)
        self.exit.bind("<ButtonRelease-1>", self.exit_release)

    def exit_enter(self, event):
        self.exit.configure(bg=Color.red)
        self.exit.bind("<ButtonPress-1>", self.exit_press)

    def exit_leave(self, event):
        self.exit.configure(bg=Color.light_black)
        self.exit.unbind("<ButtonRelease-1>")


# create a custom border for window
class CustomBorder(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        csx = Window.width
        csy = Window.height
        self.canvas_border = tk.Canvas(parent, width=csx, height=csy, bg=Color.light_black, borderwidth=0)
        self.canvas_border.place(relx=0.5, rely=0.5, anchor="center")
        self.canvas_bg = tk.Canvas(parent, width=csx - 4, height=csy - 4, bg=Color.dark_grey, highlightthickness=0)
        self.canvas_bg.place(relx=0.5, rely=0.5, anchor="center")

        self.configure(bg=Color.light_black)


# get the window position so it can be placed in the center of the screen
class WindowPosition(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

    def set(self, w=Window.width, h=Window.height, ws_value_offset=0, hs_value_offset=0):
        ws = self.winfo_screenwidth() + ws_value_offset
        hs = self.winfo_screenheight() + hs_value_offset
        x = int((ws / 2) - (w / 2))
        y = int((hs / 2) - (h / 2))
        value = f"{w}x{h}+{x}+{y}"
        return value


# pick a appropriate color for StringVar based on the string
class ColorPicker:
    def __init__(self, string_var: str = None, clabel: str = None, pct: int = -1):
        self.string_var = string_var
        self.clabel = clabel
        self.pct = pct
        self.pick()

    def pick(self):
        if self.string_var.get() == "True":
            self.clabel.configure(fg=Color.green)
        if self.string_var.get() == "False":
            self.clabel.configure(fg=Color.red)
        if self.string_var.get() == "Both":
            self.clabel.configure(fg=Color.blue)
        if self.pct in range(75, 100):
            self.clabel.configure(fg=Color.green)
        if self.pct in range(50, 75):
            self.clabel.configure(fg=Color.green_brown)
        if self.pct in range(25, 50):
            self.clabel.configure(fg=Color.red_brown)
        if self.pct in range(0, 25):
            self.clabel.configure(fg=Color.red)
