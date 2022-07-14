import os
import sys
import tkinter as tk
import webbrowser

import src.utilities.edit_registry as edit_registry
from src.data._version import current_version
from src.utilities.current_user import got_key, is_admin, run_as_admin
from src.utilities.edit_config import set_default_values, update_json
from src.utilities.fetch_config import get
from src.utilities.updates import check_for_updates

if is_admin():
    if got_key() is False:
        set_default_values()
        edit_registry.add_context_menu()
elif got_key:
    run_as_admin()
    exit()

window_width = 560
window_height = 530
tk_bg = "#1b1d22"
tk_lbg = "#4c4c4c"
tk_fg = "#bdbdbd"
tk_bc = "#121417"
tk_ec = "#494B52"
tk_font8b = "Cascadia 8 bold"
tk_font20b = "Cascadia 20 bold"
languages = get("languages")
language, lang_abbr = get("language")
precentage = get("percentage")
terminal_focus = get("terminal_focus")
hearing_impared = get("hearing_impaired")
cm_icon = get("cm_icon")


def set_window_position(w=window_width, h=window_height):
    # get screen width and height
    ws = root.winfo_screenwidth()  # width of the screen
    hs = root.winfo_screenheight()  # height of the screen

    # calculate x and y coordinates for the Tk root window
    x = int((ws / 2) - (w / 2))
    y = int((hs / 2) - (h / 2))
    value = f"{w}x{h}+{x}+{y}"
    return value


class MenuTitle(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.create_label("Menu", 1, 1, "nsew", tk_font20b)
        self.configure(bg=tk_bg)

    def create_label(self, t=None, r=1, c=1, p="nsew", f=tk_font20b):

        label = tk.Label(self, text=t, anchor="w")
        label.configure(bg=tk_bg, fg=tk_fg, font=f)
        label.grid(row=r, column=c, sticky=p, padx=2, pady=2)


class SelectLanguage(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        svar = tk.StringVar()
        svar.set(f"{language}, {lang_abbr}")
        number_of_buttons = len(languages)
        self.svar = svar
        _xstr = " " * 50
        _rowcountert = 0
        _colcountert = 1
        for i in range(1, 4):
            self.create_label(t=_xstr, r=0, c=i, f=tk_font8b)
        self.create_label(t="Selected language", r=1, c=1, f=tk_font8b)
        self.create_label(r=1, c=2, f=tk_font8b)
        for i in range(number_of_buttons):
            _rowcountert += 1
            if _rowcountert == 8:
                _colcountert += 1
                _rowcountert = 1
            self.create_button(r=_rowcountert + 1, c=_colcountert, x=i)
        self.configure(bg=tk_bg)

    def set_language(self, event):
        btn = event.widget
        self.svar.set(btn.cget("text"))
        update_svar = self.svar.get()
        update_json("language", update_svar)

    def create_label(self, t=None, r=1, c=1, p="nsew", f=tk_font8b):
        if t is None:
            label = tk.Label(self, textvariable=self.svar, anchor="center")
        else:
            label = tk.Label(self, text=t, anchor="w")
        label.configure(bg=tk_bg, fg=tk_fg, font=f)
        label.grid(row=r, column=c, sticky=p, padx=2, pady=2)

    def create_button(self, r=0, c=0, x=None):
        button = tk.Button(self, text=languages[x], height=1, width=24, bd=0)
        button.configure(bg=tk_bc, fg=tk_fg, font=tk_font8b)
        button.grid(row=r, column=c, padx=2, pady=2)
        button.bind("<Button-1>", self.set_language)


class SelectPercentage(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        svar = tk.StringVar()
        svar.set(f"{precentage} %")

        self.svar = svar
        _xstr = " " * 50
        for i in range(1, 4):
            self.create_label(t=_xstr, r=0, c=i, f=tk_font8b)
            if i >= 3:
                self.create_label(t=_xstr, r=0, c=i, f=tk_font8b)

        self.create_label(t="Selected threshold", r=1, c=1, f=tk_font8b)
        self.create_label(r=1, c=2, f=tk_font8b)

        self.create_button(r=1, c=3, x="+")
        self.create_button(r=1, c=3, x="-")

        self.configure(bg=tk_bg)

        self._add = precentage

    def b_add(self, event):

        self._add += 5 if self._add < 100 else 0
        self.svar.set(f"{self._add} %")
        update_svar = self.svar.get().split(" ")[0]
        update_json("precentage_pass", update_svar)

    def b_sub(self, event):
        self._add -= 5 if self._add > 0 else 0
        self.svar.set(f"{self._add} %")
        update_svar = self.svar.get().split(" ")[0]
        update_json("precentage_pass", update_svar)

    def create_label(self, t=None, r=1, c=1, p="nsew", f=tk_font8b):
        if t is None:
            label = tk.Label(self, textvariable=self.svar, anchor="center")
        else:
            label = tk.Label(self, text=t, anchor="w")
        label.configure(bg=tk_bg, fg=tk_fg, font=f)
        label.grid(row=r, column=c, sticky=p, padx=2, pady=2)

    def create_button(self, r=0, c=0, x=None):
        button = tk.Button(self, text=x, height=1, width=8, bd=0)
        button.configure(bg=tk_bc, fg=tk_fg, font=tk_font8b)
        if x == "+":
            button.grid(row=r, column=c, padx=5, pady=2, sticky="e")
            button.bind("<Button-1>", self.b_add)
        elif x == "-":
            button.grid(row=r, column=c, padx=5, pady=2, sticky="w")
            button.bind("<Button-1>", self.b_sub)


class HearingImparedSubs(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        svar = tk.StringVar()
        svar.set(f"{hearing_impared}")

        self.svar = svar
        _xstr = " " * 50
        for i in range(1, 4):
            self.create_label(t=_xstr, r=0, c=i, f=tk_font8b)
            if i >= 3:
                self.create_label(t=_xstr, r=0, c=i, f=tk_font8b)

        self.create_label(t="Use HI-Subtitles", r=1, c=1, f=tk_font8b)
        self.create_label(r=1, c=2, f=tk_font8b)

        self.create_button(r=1, c=3, x="Both")
        self.create_button(r=1, c=3, x="True")
        self.create_button(r=1, c=3, x="False")

        self.configure(bg=tk_bg)

    def b_true(self, event):
        self.svar.set(f"True")
        update_svar = self.svar.get()
        update_json("hearing_impaired", update_svar)

    def b_false(self, event):
        self.svar.set(f"False")
        update_svar = self.svar.get().split(" ")[0]
        update_json("hearing_impaired", update_svar)

    def b_both(self, event):
        self.svar.set(f"Both")
        update_svar = self.svar.get().split(" ")[0]
        update_json("hearing_impaired", update_svar)

    def create_label(self, t=None, r=1, c=1, p="nsew", f=tk_font8b):
        if t is None:
            label = tk.Label(self, textvariable=self.svar, anchor="center")
        else:
            label = tk.Label(self, text=t, anchor="w")
        label.configure(bg=tk_bg, fg=tk_fg, font=f)
        label.grid(row=r, column=c, sticky=p, padx=2, pady=2)

    def create_button(self, r=0, c=0, x=None):
        button = tk.Button(self, text=x, height=1, width=6, bd=0)
        button.configure(bg=tk_bc, fg=tk_fg, font=tk_font8b)
        if x == "True":
            button.grid(row=r, column=c, padx=5, pady=2, sticky="e")
            button.bind("<Button-1>", self.b_true)
        elif x == "False":
            button.grid(row=r, column=c, padx=5, pady=2, sticky="w")
            button.bind("<Button-1>", self.b_false)
        elif x == "Both":
            button.grid(row=r, column=c, padx=2, pady=2)
            button.bind("<Button-1>", self.b_both)


class ShowContextMenuIcon(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        svar = tk.StringVar()
        svar.set(f"{cm_icon}")

        self.svar = svar
        _xstr = " " * 50
        for i in range(1, 4):
            self.create_label(t=_xstr, r=0, c=i, f=tk_font8b)
            if i >= 3:
                self.create_label(t=_xstr, r=0, c=i, f=tk_font8b)

        self.create_label(t="Show context menu icon", r=1, c=1, f=tk_font8b)
        self.create_label(r=1, c=2, f=tk_font8b)

        self.create_button(r=1, c=3, x="True")
        self.create_button(r=1, c=3, x="False")

        self.configure(bg=tk_bg)

    def b_true(self, event):
        self.svar.set(f"True")
        update_svar = self.svar.get()
        update_json("context_menu_icon", update_svar)
        from src.utilities import edit_registry

        edit_registry.context_menu_icon()

    def b_false(self, event):
        self.svar.set(f"False")
        update_svar = self.svar.get()
        update_json("context_menu_icon", update_svar)
        from src.utilities import edit_registry

        edit_registry.context_menu_icon()

    def create_label(self, t=None, r=1, c=1, p="nsew", f=tk_font8b):
        if t is None:
            label = tk.Label(self, textvariable=self.svar, anchor="center")
        else:
            label = tk.Label(self, text=t, anchor="w")
        label.configure(bg=tk_bg, fg=tk_fg, font=f)
        label.grid(row=r, column=c, sticky=p, padx=2, pady=2)

    def create_button(self, r=0, c=0, x=None):
        button = tk.Button(self, text=x, height=1, width=6, bd=0)
        button.configure(bg=tk_bc, fg=tk_fg, font=tk_font8b)
        if x == "True":
            button.grid(row=r, column=c, padx=5, pady=2, sticky="e")
            button.bind("<Button-1>", self.b_true)
        elif x == "False":
            button.grid(row=r, column=c, padx=5, pady=2, sticky="w")
            button.bind("<Button-1>", self.b_false)


class ShowTerminalOnSearch(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        svar = tk.StringVar()
        svar.set(f"{cm_icon}")

        self.svar = svar
        _xstr = " " * 50
        for i in range(1, 4):
            self.create_label(t=_xstr, r=0, c=i, f=tk_font8b)
            if i >= 3:
                self.create_label(t=_xstr, r=0, c=i, f=tk_font8b)

        self.create_label(t="Terminal while searching", r=1, c=1, f=tk_font8b)
        self.create_label(r=1, c=2, f=tk_font8b)

        self.create_button(r=1, c=3, x="True")
        self.create_button(r=1, c=3, x="False")

        self.configure(bg=tk_bg)

    def b_true(self, event):
        self.svar.set(f"True")
        update_svar = self.svar.get()
        update_json("terminal_focus", update_svar)
        edit_registry.write_command_subkey()

    def b_false(self, event):
        self.svar.set(f"False")
        update_svar = self.svar.get()
        update_json("terminal_focus", update_svar)
        edit_registry.write_command_subkey()

    def create_label(self, t=None, r=1, c=1, p="nsew", f=tk_font8b):
        if t is None:
            label = tk.Label(self, textvariable=self.svar, anchor="center")
        else:
            label = tk.Label(self, text=t, anchor="w")
        label.configure(bg=tk_bg, fg=tk_fg, font=f)
        label.grid(row=r, column=c, sticky=p, padx=2, pady=2)

    def create_button(self, r=0, c=0, x=None):
        button = tk.Button(self, text=x, height=1, width=6, bd=0)
        button.configure(bg=tk_bc, fg=tk_fg, font=tk_font8b)
        if x == "True":
            button.grid(row=r, column=c, padx=5, pady=2, sticky="e")
            button.bind("<Button-1>", self.b_true)
        elif x == "False":
            button.grid(row=r, column=c, padx=5, pady=2, sticky="w")
            button.bind("<Button-1>", self.b_false)


class CheckForUpdates(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        svar = tk.StringVar()
        version = current_version()
        svar.set(f"")

        self.svar = svar
        _xstr = " " * 50
        for i in range(1, 4):
            self.create_label(t=_xstr, r=0, c=i, f=tk_font8b)
            if i >= 3:
                self.create_label(t=_xstr, r=0, c=i, f=tk_font8b)

        self.create_label(t=f"Subsearch v{version}", r=1, c=1, f=tk_font8b)
        self.create_label(r=1, c=2, f=tk_font8b)

        self.create_button(r=1, c=3, x="Check for updates")

        self.configure(bg=tk_bg)

    def b_check(self, event):
        self.svar.set(f"Searching for updates...")
        current, latest = check_for_updates(fgui=True)
        if current == latest:
            self.svar.set(f"You are up to date")
        if current != latest:
            self.svar.set(f"New version available!")
            self.create_button(r=1, c=3, x=f"Get v{latest}", new=True)

    def b_download_update(self, event):
        webbrowser.open("https://github.com/vagabondHustler/SubSearch/releases")

    def create_label(self, t=None, r=1, c=1, p="nsew", f=tk_font8b):
        if t is None:
            label = tk.Label(self, textvariable=self.svar, anchor="center")
        else:
            label = tk.Label(self, text=t, anchor="w")
        label.configure(bg=tk_bg, fg=tk_fg, font=f)
        label.grid(row=r, column=c, sticky=p, padx=2, pady=2)

    def create_button(self, r=0, c=0, x=None, new=False):
        button = tk.Button(self, text=x, height=1, bd=0)
        button.configure(bg=tk_bc, fg=tk_fg, font=tk_font8b)
        if new:
            button.grid(row=r, column=c, padx=5, pady=2, sticky="nsew")
            button.bind("<Button-1>", self.b_download_update)
        else:
            button.grid(row=r, column=c, padx=5, pady=2, sticky="nsew")
            button.bind("<Button-1>", self.b_check)


_v = current_version()
root = tk.Tk(className=f" Subsearch")
root.iconbitmap(os.path.join(sys.path[0], r"src\data\icon.ico"))
root.geometry(set_window_position())
root.resizable(False, False)
root.configure(bg=tk_bg)

MenuTitle(root).pack()
SelectLanguage(root).pack()
HearingImparedSubs(root).pack()
SelectPercentage(root).pack()
ShowContextMenuIcon(root).pack()
ShowTerminalOnSearch(root).pack()
CheckForUpdates(root).pack()

root.mainloop()
