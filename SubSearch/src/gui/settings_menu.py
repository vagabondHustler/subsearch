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
class Tks:
    window_width: int = 660
    window_height: int = 660
    bgc: str = "#1b1d22"
    lbgc: str = "#4c4c4c"
    fgc: str = "#bdbdbd"
    buttonc: str = "#121417"
    entryc: str = "#494B52"
    font8: str = "Cascadia 8 bold"
    font8b: str = "Cascadia 8 bold"
    font10b: str = "Cascadia 10 bold"
    font20b: str = "Cascadia 20 bold"
    column_lenght50: str = " " * 58


class MenuTitle(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.create_label("Menu", 1, 1, "nsew", Tks.font20b)
        self.configure(bg=Tks.bgc)

    def create_label(self, t=None, r=1, c=1, p="nsew", f=Tks.font20b):
        label = tk.Label(self, text=t, anchor="w")
        label.configure(bg=Tks.bgc, fg=Tks.fgc, font=f)
        label.grid(row=r, column=c, sticky=p, padx=2, pady=2)

class Draw(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=Tks.bgc)

    def label(self, bg=Tks.bgc, fg=Tks.fgc, text=None, textvar=None, row=None, col=None, anchor=None, sticky=None, font=Tks.font8b, padx=2, pady=2):
        _label = tk.Label(self, text=text, textvariable=textvar, font=font, fg=fg, anchor=anchor)
        _label.configure(bg=bg, fg=fg, font=font)
        _label.grid(row=row, column=col, sticky=sticky, padx=padx, pady=pady)

    def button(self, bg=Tks.buttonc, fg=Tks.fgc, text=None, height=2, width=10, bd=0, row=None, col=None, anchor=None, sticky=None, font=Tks.font8b, padx=2, pady=2, bind_to=None):
        _button = tk.Button(self, text=text, height=height, width=width, bd=bd)
        _button.configure(bg=bg, fg=fg, font=font)
        _button.grid(row=row, column=col, padx=padx, pady=pady, sticky=sticky)
        _button.bind("<Button-1>", bind_to)


class SelectLanguage(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        lang_var = tk.StringVar()
        lang_var.set(f"{language}, {lang_abbr}")
        number_of_buttons = len(languages)
        self.lang_var = lang_var
        rowcount = 0
        colcount = 1
        for i in range(1, 4):
            Draw.label(self, text=Tks.column_lenght50, row=1, col=i, font=Tks.font8)
        Draw.label(self, text="Selected language", sticky="w", row=1, col=1, font=Tks.font8b)
        Draw.label(self, textvar=self.lang_var, row=1, col=2, font=Tks.font8b)
        for i in range(number_of_buttons):
            rowcount += 1
            if rowcount == 8:
                colcount += 1
                rowcount = 1
            Draw.button(self, text=languages[i], row=rowcount + 1, col=colcount, height=2, width=24, bind_to=self.button_set_lang)
        self.configure(bg=Tks.bgc)

    def button_set_lang(self, event):
        btn = event.widget
        self.lang_var.set(btn.cget("text"))
        update_svar = self.lang_var.get()
        update_json("language", update_svar)


class HearingImparedSubs(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        hi_var = tk.StringVar()
        hi_var.set(f"{hearing_impared}")
        self.hi_var = hi_var
        for i in range(1, 4):
            Draw.label(self, text=Tks.column_lenght50, row=1, col=i, font=Tks.font8)
        Draw.label(self, text="Hearing impaired subtitles", sticky="w", row=1, col=1, font=Tks.font8b, anchor="w")
        Draw.label(self, textvar=self.hi_var, row=1, col=2, font=Tks.font8b)
        Draw.button(self, text="True", row=1, col=3, width=7, sticky="e", bind_to=self.button_set_true)
        Draw.button(self, text="False", row=1, col=3, width=7, sticky="w", bind_to=self.button_set_false)
        Draw.button(self, text="Both", row=1, col=3, width=7, bind_to=self.button_set_both)
        self.configure(bg=Tks.bgc)

    def button_set_true(self, event):
        self.hi_var.set(f"True")
        update_svar = self.hi_var.get()
        update_json("hearing_impaired", update_svar)

    def button_set_false(self, event):
        self.hi_var.set(f"False")
        update_svar = self.hi_var.get().split(" ")[0]
        update_json("hearing_impaired", update_svar)

    def button_set_both(self, event):
        self.hi_var.set(f"Both")
        update_svar = self.hi_var.get().split(" ")[0]
        update_json("hearing_impaired", update_svar)


class SearchThreshold(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        pct_var = tk.StringVar()
        pct_var.set(f"{precentage} %")
        self._add = precentage
        self.pct_var = pct_var
        for i in range(1, 4):
            Draw.label(self, text=Tks.column_lenght50, row=1, col=i, font=Tks.font8)
        Draw.label(self, text="Search threshold", sticky="w", row=1, col=1, font=Tks.font8b)
        Draw.label(self, textvar=self.pct_var, row=1, col=2, font=Tks.font8b)
        Draw.button(self, text="+", row=1, col=3, sticky="e", bind_to=self.button_add_5)
        Draw.button(self, text="-", row=1, col=3, sticky="w", bind_to=self.button_sub_5)
        self.configure(bg=Tks.bgc)

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


class ShowContextMenu(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        context_menu = tk.StringVar()
        context_menu.set(f"True")
        self.context_menu = context_menu
        for i in range(1, 4):
            Draw.label(self, text=Tks.column_lenght50, row=1, col=i, font=Tks.font8)
        Draw.label(self, text="Show context menu", row=1, col=1, sticky="w", font=Tks.font8b)
        Draw.label(self, textvar=self.context_menu, row=1, col=2, font=Tks.font8b, anchor="center")
        Draw.button(self, text="True", row=1, col=3, sticky="e", bind_to=self.button_set_true)
        Draw.button(self, text="False", row=1, col=3, sticky="w", bind_to=self.button_set_false)
        self.configure(bg=Tks.bgc)

    def button_set_true(self, event):
        self.context_menu.set(f"True")
        from src.utilities import edit_registry

        edit_registry.restore_context_menu()

    def button_set_false(self, event):
        self.context_menu.set(f"False")
        from src.utilities import edit_registry

        edit_registry.remove_context_menu()


class ShowContextMenuIcon(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        cmi_var = tk.StringVar()
        cmi_var.set(f"{cm_icon}")
        self.cmi_var = cmi_var
        for i in range(1, 4):
            Draw.label(self, text=Tks.column_lenght50, row=1, col=i, font=Tks.font8)
        Draw.label(self, text="Show context menu icon", row=1, col=1, sticky="w", font=Tks.font8b)
        Draw.label(self, textvar=self.cmi_var, row=1, col=2, font=Tks.font8b)
        Draw.button(self, text="True", row=1, col=3, sticky="e", bind_to=self.button_set_true)
        Draw.button(self, text="False", row=1, col=3, sticky="w", bind_to=self.button_set_false)
        self.configure(bg=Tks.bgc)

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


class ShowTerminalOnSearch(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        terminal_var = tk.StringVar()
        terminal_var.set(f"{cm_icon}")
        self.terminal_var = terminal_var
        for i in range(1, 4):
            Draw.label(self, text=Tks.column_lenght50, row=1, col=i, font=Tks.font8)
        Draw.label(self, text="Show terminal on search", row=1, col=1, sticky="w", font=Tks.font8b)
        Draw.label(self, textvar=self.terminal_var, row=1, col=2, font=Tks.font8b)
        Draw.button(self, text="True", row=1, col=3, sticky="e", bind_to=self.button_set_true)
        Draw.button(self, text="False", row=1, col=3, sticky="w", bind_to=self.button_set_false)
        self.configure(bg=Tks.bgc)

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


class CheckForUpdates(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        updates_var = tk.StringVar()
        c_version = current_version()
        updates_var.set(f"")
        self.updates_var = updates_var
        for i in range(1, 4):
            Draw.label(self, text=Tks.column_lenght50, row=1, col=i, font=Tks.font8)
        Draw.label(self, text=f"SubScene version {c_version}", row=1, col=1, sticky="w", font=Tks.font8b)
        Draw.label(self, textvar=self.updates_var, row=1, col=2, font=Tks.font8b)
        Draw.button(self, text="Check for updates", row=1, col=3, height=2, width=18, bind_to=self.button_check)
        self.configure(bg=Tks.bgc)

    def button_check(self, event):
        self.updates_var.set(f"Searching for updates...")
        current, latest = check_for_updates(fgui=True)
        if current == latest:
            self.updates_var.set(f"You are up to date!")
        if current != latest:
            self.updates_var.set(f"New version available!")
            Draw.button(self, text=f"Get v{latest}", row=1, col=3, height=2, width=18, bind_to=self.button_download)

    def button_download(self, event):
        webbrowser.open("https://github.com/vagabondHustler/SubSearch/releases")


def set_window_position(w=Tks.window_width, h=Tks.window_height):
    # get screen width and height
    ws = root.winfo_screenwidth()  # width of the screen
    hs = root.winfo_screenheight()  # height of the screen

    # calculate x and y coordinates for the Tk root window
    x = int((ws / 2) - (w / 2))
    y = int((hs / 2) - (h / 2))
    value = f"{w}x{h}+{x}+{y}"
    return value


c_verison = current_version()
root = tk.Tk(className=f" SubSearch")
root.iconbitmap(os.path.join(sys.path[0], r"src\data\icon.ico"))
root.geometry(set_window_position())
root.resizable(False, False)
root.configure(bg=Tks.bgc)


tk.Frame(root, bg=Tks.bgc).pack(anchor="center", expand=True)
SelectLanguage(root).pack(anchor="center")
tk.Frame(root, bg=Tks.bgc).pack(anchor="center", expand=True)
HearingImparedSubs(root).pack(anchor="center")
SearchThreshold(root).pack(anchor="center")
tk.Frame(root, bg=Tks.bgc).pack(anchor="center", expand=True)
ShowContextMenu(root).pack(anchor="center")
ShowContextMenuIcon(root).pack(anchor="center")
ShowTerminalOnSearch(root).pack(anchor="center")
tk.Frame(root, bg=Tks.bgc).pack(anchor="center", expand=True)
CheckForUpdates(root).pack(anchor="center")
tk.Frame(root, bg=Tks.bgc).pack(anchor="center", expand=True)

root.mainloop()
