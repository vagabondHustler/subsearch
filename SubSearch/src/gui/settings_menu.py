from dataclasses import dataclass
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

languages = get("languages")
language, lang_abbr = get("language")
precentage = get("percentage")
terminal_focus = get("terminal_focus")
hearing_impared = get("hearing_impaired")
cm_icon = get("cm_icon")


@dataclass
class TkSettings:
    window_width: int = 560
    window_height: int = 530
    bg_color: str = "#1b1d22"
    light_bg_color: str = "#4c4c4c"
    fg_color: str = "#bdbdbd"
    button_color: str = "#121417"
    entry_color: str = "#494B52"
    font8b: str = "Cascadia 8 bold"
    font20b: str = "Cascadia 20 bold"
    column_lenght50: str = " " * 50


class MenuTitle(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.create_label("Menu", 1, 1, "nsew", TkSettings.font20b)
        self.configure(bg=TkSettings.bg_color)

    def create_label(self, t=None, r=1, c=1, p="nsew", f=TkSettings.font20b):

        label = tk.Label(self, text=t, anchor="w")
        label.configure(bg=TkSettings.bg_color, fg=TkSettings.fg_color, font=f)
        label.grid(row=r, column=c, sticky=p, padx=2, pady=2)


class SelectLanguage(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        lang_var = tk.StringVar()
        lang_var.set(f"{language}, {lang_abbr}")
        number_of_buttons = len(languages)
        self.lang_var = lang_var
        _rowcountert = 0
        _colcountert = 1
        for i in range(1, 4):
            self.create_label(t=TkSettings.column_lenght50, r=0, c=i, f=TkSettings.font8b)
        self.create_label(t="Selected language", r=1, c=1, f=TkSettings.font8b)
        self.create_label(r=1, c=2, f=TkSettings.font8b)
        for i in range(number_of_buttons):
            _rowcountert += 1
            if _rowcountert == 8:
                _colcountert += 1
                _rowcountert = 1
            self.create_button(r=_rowcountert + 1, c=_colcountert, x=i)
        self.configure(bg=TkSettings.bg_color)

    def button_set_lang(self, event):
        btn = event.widget
        self.lang_var.set(btn.cget("text"))
        update_svar = self.lang_var.get()
        update_json("language", update_svar)

    def create_label(self, t=None, r=1, c=1, p="nsew", f=TkSettings.font8b):
        if t is None:
            label = tk.Label(self, textvariable=self.lang_var, anchor="center")
        else:
            label = tk.Label(self, text=t, anchor="w")
        label.configure(bg=TkSettings.bg_color, fg=TkSettings.fg_color, font=f)
        label.grid(row=r, column=c, sticky=p, padx=2, pady=2)

    def create_button(self, r=0, c=0, x=None):
        button = tk.Button(self, text=languages[x], height=1, width=24, bd=0)
        button.configure(bg=TkSettings.button_color, fg=TkSettings.fg_color, font=TkSettings.font8b)
        button.grid(row=r, column=c, padx=2, pady=2)
        button.bind("<Button-1>", self.button_set_lang)


class SelectPercentage(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        pct_var = tk.StringVar()
        pct_var.set(f"{precentage} %")

        self.pct_var = pct_var
        TkSettings.column_lenght50 = " " * 50
        for i in range(1, 4):
            self.create_label(t=TkSettings.column_lenght50, r=0, c=i, f=TkSettings.font8b)
            if i >= 3:
                self.create_label(t=TkSettings.column_lenght50, r=0, c=i, f=TkSettings.font8b)

        self.create_label(t="Selected threshold", r=1, c=1, f=TkSettings.font8b)
        self.create_label(r=1, c=2, f=TkSettings.font8b)

        self.create_button(r=1, c=3, x="+")
        self.create_button(r=1, c=3, x="-")

        self.configure(bg=TkSettings.bg_color)

        self._add = precentage

    def button_add_5(self, event):
        self._add += 5 if self._add < 100 else 0
        self.pct_var.set(f"{self._add} %")
        update_svar = int(self.pct_var.get().split(" ")[0])
        update_json("precentage_pass", update_svar)

    def button_sub_5(self, event):
        self._add -= 5 if self._add > 0 else 0
        self.pct_var.set(f"{self._add} %")
        update_svar = int(self.pct_var.get().split(" ")[0])
        update_json("precentage_pass", update_svar)

    def create_label(self, t=None, r=1, c=1, p="nsew", f=TkSettings.font8b):
        if t is None:
            label = tk.Label(self, textvariable=self.pct_var, anchor="center")
        else:
            label = tk.Label(self, text=t, anchor="w")
        label.configure(bg=TkSettings.bg_color, fg=TkSettings.fg_color, font=f)
        label.grid(row=r, column=c, sticky=p, padx=2, pady=2)

    def create_button(self, r=0, c=0, x=None):
        button = tk.Button(self, text=x, height=1, width=8, bd=0)
        button.configure(bg=TkSettings.button_color, fg=TkSettings.fg_color, font=TkSettings.font8b)
        if x == "+":
            button.grid(row=r, column=c, padx=5, pady=2, sticky="e")
            button.bind("<Button-1>", self.button_add_5)
        elif x == "-":
            button.grid(row=r, column=c, padx=5, pady=2, sticky="w")
            button.bind("<Button-1>", self.button_sub_5)


class HearingImparedSubs(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        hi_var = tk.StringVar()
        hi_var.set(f"{hearing_impared}")
        self.hi_var = hi_var
        for i in range(1, 4):
            self.create_label(t=TkSettings.column_lenght50, r=0, c=i, f=TkSettings.font8b)
            if i >= 3:
                self.create_label(t=TkSettings.column_lenght50, r=0, c=i, f=TkSettings.font8b)

        self.create_label(t="Use HI-Subtitles", r=1, c=1, f=TkSettings.font8b)
        self.create_label(r=1, c=2, f=TkSettings.font8b)
        self.create_button(r=1, c=3, x="Both")
        self.create_button(r=1, c=3, x="True")
        self.create_button(r=1, c=3, x="False")
        self.configure(bg=TkSettings.bg_color)

    def button_set_true(self, event):
        self.hi_var.set(f"True")
        update_svar = self.hi_var.get()
        update_json("hearing_impaired", update_svar)

    def button_set_false(self, event):
        self.hi_var.set(f"False")
        update_svar = self.hi_var.get().split(" ")[0]
        update_json("hearing_impaired", update_svar)

    def button_both(self, event):
        self.hi_var.set(f"Both")
        update_svar = self.hi_var.get().split(" ")[0]
        update_json("hearing_impaired", update_svar)

    def create_label(self, t=None, r=1, c=1, p="nsew", f=TkSettings.font8b):
        if t is None:
            label = tk.Label(self, textvariable=self.hi_var, anchor="center")
        else:
            label = tk.Label(self, text=t, anchor="w")
        label.configure(bg=TkSettings.bg_color, fg=TkSettings.fg_color, font=f)
        label.grid(row=r, column=c, sticky=p, padx=2, pady=2)

    def create_button(self, r=0, c=0, x=None):
        button = tk.Button(self, text=x, height=1, width=6, bd=0)
        button.configure(bg=TkSettings.button_color, fg=TkSettings.fg_color, font=TkSettings.font8b)
        if x == "True":
            button.grid(row=r, column=c, padx=5, pady=2, sticky="e")
            button.bind("<Button-1>", self.button_set_true)
        elif x == "False":
            button.grid(row=r, column=c, padx=5, pady=2, sticky="w")
            button.bind("<Button-1>", self.button_set_false)
        elif x == "Both":
            button.grid(row=r, column=c, padx=2, pady=2)
            button.bind("<Button-1>", self.button_both)


class ShowContextMenuIcon(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        cmi_var = tk.StringVar()
        cmi_var.set(f"{cm_icon}")
        self.cmi_var = cmi_var
        TkSettings.column_lenght50 = " " * 50
        for i in range(1, 4):
            self.create_label(t=TkSettings.column_lenght50, r=0, c=i, f=TkSettings.font8b)
            if i >= 3:
                self.create_label(t=TkSettings.column_lenght50, r=0, c=i, f=TkSettings.font8b)
        self.create_label(t="Show context menu icon", r=1, c=1, f=TkSettings.font8b)
        self.create_label(r=1, c=2, f=TkSettings.font8b)
        self.create_button(r=1, c=3, x="True")
        self.create_button(r=1, c=3, x="False")
        self.configure(bg=TkSettings.bg_color)

    def button_set_true(self, event):
        self.cmi_var.set(f"True")
        update_svar = self.cmi_var.get()
        update_json("context_menu_icon", update_svar)
        from src.utilities import edit_registry

        edit_registry.context_menu_icon()

    def button_set_false(self, event):
        self.cmi_var.set(f"False")
        update_svar = self.cmi_var.get()
        update_json("context_menu_icon", update_svar)
        from src.utilities import edit_registry

        edit_registry.context_menu_icon()

    def create_label(self, t=None, r=1, c=1, p="nsew", f=TkSettings.font8b):
        if t is None:
            label = tk.Label(self, textvariable=self.cmi_var, anchor="center")
        else:
            label = tk.Label(self, text=t, anchor="w")
        label.configure(bg=TkSettings.bg_color, fg=TkSettings.fg_color, font=f)
        label.grid(row=r, column=c, sticky=p, padx=2, pady=2)

    def create_button(self, r=0, c=0, x=None):
        button = tk.Button(self, text=x, height=1, width=6, bd=0)
        button.configure(bg=TkSettings.button_color, fg=TkSettings.fg_color, font=TkSettings.font8b)
        if x == "True":
            button.grid(row=r, column=c, padx=5, pady=2, sticky="e")
            button.bind("<Button-1>", self.button_set_true)
        elif x == "False":
            button.grid(row=r, column=c, padx=5, pady=2, sticky="w")
            button.bind("<Button-1>", self.button_set_false)


class ShowTerminalOnSearch(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        terminal_var = tk.StringVar()
        terminal_var.set(f"{cm_icon}")
        self.terminal_var = terminal_var
        TkSettings.column_lenght50 = " " * 50
        for i in range(1, 4):
            self.create_label(t=TkSettings.column_lenght50, r=0, c=i, f=TkSettings.font8b)
            if i >= 3:
                self.create_label(t=TkSettings.column_lenght50, r=0, c=i, f=TkSettings.font8b)

        self.create_label(t="Terminal while searching", r=1, c=1, f=TkSettings.font8b)
        self.create_label(r=1, c=2, f=TkSettings.font8b)
        self.create_button(r=1, c=3, x="True")
        self.create_button(r=1, c=3, x="False")
        self.configure(bg=TkSettings.bg_color)

    def button_set_true(self, event):
        self.terminal_var.set(f"True")
        update_svar = self.terminal_var.get()
        update_json("terminal_focus", update_svar)
        edit_registry.write_command_subkey()

    def button_set_false(self, event):
        self.terminal_var.set(f"False")
        update_svar = self.terminal_var.get()
        update_json("terminal_focus", update_svar)
        edit_registry.write_command_subkey()

    def create_label(self, t=None, r=1, c=1, p="nsew", f=TkSettings.font8b):
        if t is None:
            label = tk.Label(self, textvariable=self.terminal_var, anchor="center")
        else:
            label = tk.Label(self, text=t, anchor="w")
        label.configure(bg=TkSettings.bg_color, fg=TkSettings.fg_color, font=f)
        label.grid(row=r, column=c, sticky=p, padx=2, pady=2)

    def create_button(self, r=0, c=0, x=None):
        button = tk.Button(self, text=x, height=1, width=6, bd=0)
        button.configure(bg=TkSettings.button_color, fg=TkSettings.fg_color, font=TkSettings.font8b)
        if x == "True":
            button.grid(row=r, column=c, padx=5, pady=2, sticky="e")
            button.bind("<Button-1>", self.button_set_true)
        elif x == "False":
            button.grid(row=r, column=c, padx=5, pady=2, sticky="w")
            button.bind("<Button-1>", self.button_set_false)


class CheckForUpdates(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        updates_var = tk.StringVar()
        c_version = current_version()
        updates_var.set(f"")
        self.updates_var = updates_var
        TkSettings.column_lenght50 = " " * 50
        for i in range(1, 4):
            self.create_label(t=TkSettings.column_lenght50, r=0, c=i, f=TkSettings.font8b)
            if i >= 3:
                self.create_label(t=TkSettings.column_lenght50, r=0, c=i, f=TkSettings.font8b)

        self.create_label(t=f"Subsearch v{c_version}", r=1, c=1, f=TkSettings.font8b)
        self.create_label(r=1, c=2, f=TkSettings.font8b)
        self.create_button(r=1, c=3, x="Check for updates")
        self.configure(bg=TkSettings.bg_color)

    def b_check(self, event):
        self.updates_var.set(f"Searching for updates...")
        current, latest = check_for_updates(fgui=True)
        if current == latest:
            self.updates_var.set(f"You are up to date")
        if current != latest:
            self.updates_var.set(f"New version available!")
            self.create_button(r=1, c=3, x=f"Get v{latest}", new=True)

    def b_download_update(self, event):
        webbrowser.open("https://github.com/vagabondHustler/SubSearch/releases")

    def create_label(self, t=None, r=1, c=1, p="nsew", f=TkSettings.font8b):
        if t is None:
            label = tk.Label(self, textvariable=self.updates_var, anchor="center")
        else:
            label = tk.Label(self, text=t, anchor="w")
        label.configure(bg=TkSettings.bg_color, fg=TkSettings.fg_color, font=f)
        label.grid(row=r, column=c, sticky=p, padx=2, pady=2)

    def create_button(self, r=0, c=0, x=None, new=False):
        button = tk.Button(self, text=x, height=1, bd=0)
        button.configure(bg=TkSettings.button_color, fg=TkSettings.fg_color, font=TkSettings.font8b)
        if new:
            button.grid(row=r, column=c, padx=5, pady=2, sticky="nsew")
            button.bind("<Button-1>", self.b_download_update)
        else:
            button.grid(row=r, column=c, padx=5, pady=2, sticky="nsew")
            button.bind("<Button-1>", self.b_check)


def set_window_position(w=TkSettings.window_width, h=TkSettings.window_height):
    # get screen width and height
    ws = root.winfo_screenwidth()  # width of the screen
    hs = root.winfo_screenheight()  # height of the screen

    # calculate x and y coordinates for the Tk root window
    x = int((ws / 2) - (w / 2))
    y = int((hs / 2) - (h / 2))
    value = f"{w}x{h}+{x}+{y}"
    return value


c_verison = current_version()
root = tk.Tk(className=f" Subsearch")
root.iconbitmap(os.path.join(sys.path[0], r"src\data\icon.ico"))
root.geometry(set_window_position())
root.resizable(False, False)
root.configure(bg=TkSettings.bg_color)

MenuTitle(root).pack()
SelectLanguage(root).pack()
HearingImparedSubs(root).pack()
SelectPercentage(root).pack()
ShowContextMenuIcon(root).pack()
ShowTerminalOnSearch(root).pack()
CheckForUpdates(root).pack()

root.mainloop()
