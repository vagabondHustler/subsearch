import ctypes
import sys
import tkinter as tk
from dataclasses import dataclass

from src.scraper.subscene_soup import get_download_url
from src.utilities.file_manager import (clean_up, download_zip_auto,
                                        extract_zips)
from src.utilities.local_paths import cwd, root_directory
from src.utilities.version import current_version


@dataclass
class Tks:
    """
    Dataclass with often used values for the graphical user interface
    """

    window_width: int = 760
    window_height: int = 760
    bg: str = "#1b1d22"
    bgl: str = "#4c4c4c"
    fg: str = "#bdbdbd"
    fge: str = "#c5895e"
    bc: str = "#121417"
    abg: str = "#16181c"
    abg_disabled: str = "#303030"
    font8: str = "Cascadia 8"
    font8b: str = "Cascadia 8 bold"
    font10b: str = "Cascadia 8 bold"
    font10b: str = "Cascadia 10 bold"
    font20b: str = "Cascadia 20 bold"
    col58: str = " " * 58


class Create(tk.Frame):
    def __init__(self, parent) -> None:
        tk.Frame.__init__(self, parent)
        self.configure(bg=Tks.bg)

    # create a basic label
    def label(
        self,
        bg=Tks.bg,
        fg=Tks.fg,
        text=None,
        textvar=None,
        row=None,
        col=None,
        anchor=None,
        sticky=None,
        font=Tks.font8b,
        padx=2,
        pady=2,
    ) -> str:
        _label = tk.Label(self, text=text, textvariable=textvar, font=font, fg=fg, anchor=anchor)
        _label.configure(bg=bg, fg=fg, font=font)
        _label.grid(row=row, column=col, sticky=sticky, padx=padx, pady=pady)
        return _label
    
    # create a basic button
    def button(
        self,
        bg=Tks.bc,
        abgc=Tks.abg,
        bge=Tks.abg,
        fg=Tks.fg,
        fge=Tks.fge,
        text=None,
        height=2,
        width=10,
        bd=0,
        row=None,
        col=None,
        sticky=None,
        font=Tks.font8b,
        padx=2,
        pady=2,
        bind_to=None,
        tip_show=False,
        tip_text=None,
    ) -> str:
        _button = tk.Button(self, text=text, height=height, width=width, bd=bd)
        _button.configure(activebackground=abgc, bg=bg, fg=fg, font=font)
        _button.grid(row=row, column=col, padx=padx, pady=pady, sticky=sticky)
        _button.bind("<Button-1>", bind_to)
        tip = Hovertip(_button, tip_text) if tip_show else None

        def button_enter(self) -> None:
            _button.configure(bg=bge, fg=fge, font=font)
            tip.showtip() if tip_show else None

        def button_leave(self) -> None:
            _button.configure(bg=bg, fg=fg, font=font)
            tip.hidetip() if tip_show else None

        _button.bind("<Enter>", button_enter)
        _button.bind("<Leave>", button_leave)
        return _button

# replace the regular windows-style title bar with a custom one
class CustomTitleBar(tk.Frame):
    def __init__(self, parent) -> None:
        tk.Frame.__init__(self, parent)
        self.after(10, self.remove_titlebar, root)
        self.parent = parent
        self._offsetx = 0
        self._offsety = 0
        root.focus_force()
        root.overrideredirect(True)
        button = Create.button(
            self,
            text="X",
            row=0,
            col=0,
            height=1,
            width=2,
            abgc="#cd2e3e",
            bge="#a72633",
            fge=Tks.fg,
            font=Tks.font10b,
            pady=5,
            padx=5,
            bind_to=self.tk_exit_press,
        )
        label = tk.Label(
            root,
            text=" SubSearch",
            height=2,
            bg=Tks.bc,
            fg=Tks.fg,
            font=Tks.font10b,
            justify="left",
            anchor="w",
            width=Tks.window_width,
        )
        label.place(bordermode="outside", x=0, y=0)
        label.lower()
        self.button = button
        self.label = label

        label.bind("<Button-1>", self.titlebar_press)
        label.bind("<B1-Motion>", self.titlebar_drag)

        self.configure(bg=Tks.bc)

    def window_pos(self, parent, w: int = 80, h: int = 48) -> str:
        ws = parent.winfo_screenwidth()
        hs = parent.winfo_screenheight()

        x = int((ws / 2) - (w / 2))
        y = int((hs / 2) - (h / 2))
        value = f"{w}x{h}+{x}+{y}"
        return value

    def remove_titlebar(self, parent) -> None:
        GWL_EXSTYLE = -20
        WS_EX_APPWINDOW = 0x00040000
        WS_EX_TOOLWINDOW = 0x00000080
        hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
        style = ctypes.windll.user32.GetWindowLongPtrW(hwnd, GWL_EXSTYLE)
        style = style & ~WS_EX_TOOLWINDOW
        style = style | WS_EX_APPWINDOW
        res = ctypes.windll.user32.SetWindowLongPtrW(hwnd, GWL_EXSTYLE, style)
        root.withdraw()
        root.after(10, root.deiconify)

    def titlebar_press(self, event) -> None:
        self._offsetx = root.winfo_pointerx() - root.winfo_rootx()
        self._offsety = root.winfo_pointery() - root.winfo_rooty()

    def titlebar_drag(self, event) -> None:
        x = self.winfo_pointerx() - self._offsetx
        y = self.winfo_pointery() - self._offsety
        root.geometry(f"+{x}+{y}")

    def tk_exit_release(self, event) -> None:
        clean_up(cwd(), "temp.txt")
        root.destroy()

    def tk_exit_press(self, event) -> None:
        self.button.bind("<ButtonRelease-1>", self.tk_exit_release)


# download said subtitle to the folder with the video file in it
class DownloadList(tk.Frame):
    def __init__(self, parent) -> None:
        tk.Frame.__init__(self, parent)
        count = 1
        input_list = tk.Listbox(
            root,
            bg=Tks.bg,
            fg=Tks.fg,
            font=Tks.font10b,
            bd=0,
            border=0,
            borderwidth=0,
        )
        input_list.place(
            height=Tks.window_height - 80,
            width=Tks.window_width - 80,
            relx=0.5,
            rely=0.525,
            bordermode="inside",
            anchor="center",
        )
        dicts_names = {}
        dicts_urls = {}
        count = 0
        for x, i in zip(range(0, len(sublist)), sublist):
            x = i.split(" ")
            match = f"{x[0]} {x[1]}"
            name = x[2]
            url = x[-1]
            txt = f"{match} {name}"
            input_list.insert(tk.END, f"{match} {name}\n")
            input_list.bind("<<ListboxSelect>>", self.download_button)
            dicts_names[count] = txt
            dicts_urls[count] = url
            self.dicts_urls = dicts_urls
            self.dicts_names = dicts_names
            self.input_list = input_list
            count += 1
        self.configure(bg=Tks.bc)

    def download_button(self, event) -> None:
        a = str(self.input_list.curselection())
        a = a.replace("(", "")
        a = a.replace(")", "")
        a = a.replace(",", "")
        _error = False
        for (number, url), (name) in zip(self.dicts_urls.items(), self.dicts_names.values()):
            if number == int(a):
                self.input_list.delete(int(number))
                self.input_list.insert(int(number), f"»»» DOWNLOADING «««")
                self.input_list.itemconfig(int(number), {"fg": "#2b609a"})
                try:
                    dl_url = get_download_url(url)
                    _name = name.replace("/", "").replace("\\", "").split(": ")
                    path = f"{cwd()}\\{_name[-1]}.zip"
                    item = path, dl_url, 1, 1
                    download_zip_auto(item)
                    if _error is False:
                        extract_zips(cwd(), ".zip")
                        clean_up(cwd(), ".zip")
                        clean_up(cwd(), ").nfo")
                        self.input_list.delete(int(number))
                        self.input_list.insert(int(number), f"✔ {name}")
                        self.input_list.itemconfig(int(number), {"fg": "#73aa4f"})
                        _error = False
                except OSError:
                    _error = True
                    self.input_list.delete(int(number))
                    self.input_list.insert(int(number), f"⚠⚠⚠ Download failed ⚠⚠⚠")
                    self.input_list.itemconfig(int(number), {"fg": "#9b3435"})


# get the window position so it can be placed in the center of the screen
def set_window_position(w=Tks.window_width, h=Tks.window_height):
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = int((ws / 2) - (w / 2))
    y = int((hs / 2) - (h / 2))
    value = f"{w}x{h}+{x}+{y}"
    return value


import os

# only runs if file is run as administrator
print(os.getcwd())
with open("temp.txt", "r") as fileopen:
    sublist = [line.strip() for line in fileopen]

if "win" in sys.platform:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)

c_verison = current_version()
root = tk.Tk(className=f" SubSearch")

icon_path = root_directory("data", "64.ico")
root.iconbitmap(icon_path)
root.geometry(set_window_position())
# root.resizable(False, False)
root.wm_attributes("-transparentcolor", "#2a2d2f")
root.configure(bg=Tks.bg)
CustomTitleBar(root).place(x=Tks.window_width - 2, y=2, bordermode="inside", anchor="ne")
tk.Frame(root, bg=Tks.bg).pack(anchor="center", expand=True)
tk.Frame(root, bg=Tks.bg).pack(anchor="center", expand=True)
tk.Frame(root, bg=Tks.bg).pack(anchor="center", expand=True)
DownloadList(root).pack(anchor="center")
tk.Frame(root, bg=Tks.bg).pack(anchor="center", expand=True)
root.mainloop()


sys.exit()
