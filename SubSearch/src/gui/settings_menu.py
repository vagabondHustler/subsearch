import ctypes
import sys
import tkinter as tk
import webbrowser
from dataclasses import dataclass

import src.utilities.edit_registry as edit_registry
from src.data._version import current_version
from src.gui.tooltip import Hovertip
from src.utilities.local_paths import cwd
from src.utilities.current_user import got_key, is_admin, run_as_admin
from src.utilities.edit_config import set_default_values, update_json
from src.utilities.fetch_config import get
from src.utilities.updates import check_for_updates

languages = get("languages")
language, lang_abbr = get("language")
precentage = get("percentage")
terminal_focus = get("terminal_focus")
hearing_impared = get("hearing_impaired")
cm_icon = get("cm_icon")


@dataclass
class Tks:
    """Data class for diffrent gui settings that are used often.

    Args:
        window_width (int) = The width of the window\n
        window_height (int) = The height of the window\n
        bgc (str) = Background color\n
        lbgc (str) = Light background color\n
        fgc (str) = Foreground color\n
        efgc (str) = Enter foreground color, when mouse enters said area\n
        buttonc (str) = Button color\n
        abgc (str) = Active background color, when object is active\n
        font8 (str) = Font Cascadia 8\n
        font8b (str) = Font Cascadia 8 bold\n
        font10b (str) = Font Cascadia 10 bold\n
        font20b (str) = Font Cascadia 20 bold\n
        column_lenght50 (str) = Fills column with 50 blank spaces"""

    window_width: int = 660
    window_height: int = 660
    bgc: str = "#1b1d22"
    lbgc: str = "#4c4c4c"
    fgc: str = "#bdbdbd"
    efgc: str = "#c5895e"
    buttonc: str = "#121417"
    abgc: str = "#16181c"
    font8: str = "Cascadia 8"
    font8b: str = "Cascadia 8 bold"
    font10b: str = "Cascadia 10 bold"
    font20b: str = "Cascadia 20 bold"
    column_lenght50: str = " " * 58


class MenuTitle(tk.Frame):
    def __init__(self, parent) -> None:
        tk.Frame.__init__(self, parent)
        self.create_label("Menu", 1, 1, "nsew", Tks.font20b)
        self.configure(bg=Tks.bgc)

    def create_label(self, t=None, r=1, c=1, p="nsew", f=Tks.font20b) -> None:
        label = tk.Label(self, text=t, anchor="w")
        label.configure(bg=Tks.bgc, fg=Tks.fgc, font=f)
        label.grid(row=r, column=c, sticky=p, padx=2, pady=2)


class Draw(tk.Frame):
    def __init__(self, parent) -> None:
        tk.Frame.__init__(self, parent)

        self.configure(bg=Tks.bgc)

    def label(
        self,
        bg=Tks.bgc,
        fg=Tks.fgc,
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

    def button(
        self,
        bg=Tks.buttonc,
        abgc=Tks.abgc,
        bgc_e=Tks.abgc,
        bgc_l=Tks.buttonc,
        fg=Tks.fgc,
        fg_e=Tks.efgc,
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
        show_tip=False,
        text_tip=None,
    ) -> str:
        _button = tk.Button(self, text=text, height=height, width=width, bd=bd)
        _button.configure(activebackground=abgc, bg=bg, fg=fg, font=font)
        _button.grid(row=row, column=col, padx=padx, pady=pady, sticky=sticky)
        _button.bind("<Button-1>", bind_to)
        tip = Hovertip(_button, text_tip) if show_tip else None

        def button_enter(self) -> None:
            _button.configure(bg=bgc_e, fg=fg_e, font=font)
            tip.showtip() if show_tip else None

        def button_leave(self) -> None:
            _button.configure(bg=bg, fg=fg, font=font)
            tip.hidetip() if show_tip else None

        _button.bind("<Enter>", button_enter)
        _button.bind("<Leave>", button_leave)
        return _button


class SelectLanguage(tk.Frame):
    def __init__(self, parent) -> None:
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

    def button_set_lang(self, event) -> None:
        btn = event.widget
        self.lang_var.set(btn.cget("text"))
        update_svar = self.lang_var.get()
        update_json("language", update_svar)


class HearingImparedSubs(tk.Frame):
    def __init__(self, parent) -> None:
        tk.Frame.__init__(self, parent)
        hi_var = tk.StringVar()
        hi_var.set(f"{hearing_impared}")
        self.hi_var = hi_var
        for i in range(1, 4):
            Draw.label(self, text=Tks.column_lenght50, row=1, col=i, font=Tks.font8)
        Draw.label(self, text="Hearing impaired subtitles", sticky="w", row=1, col=1, font=Tks.font8b, anchor="w")
        Draw.label(self, textvar=self.hi_var, row=1, col=2, font=Tks.font8b)
        Draw.button(self, text="True", row=1, col=3, width=7, sticky="e", bind_to=self.button_set_true, show_tip=True, text_tip="Only use hearing impaired subtitles")
        Draw.button(self, text="False", row=1, col=3, width=7, sticky="w", bind_to=self.button_set_false, show_tip=True, text_tip="Only use regular subtitles")
        Draw.button(self, text="Both", row=1, col=3, width=7, bind_to=self.button_set_both, show_tip=True, text_tip="Use both hearing impaired and regular subtitles")
        self.configure(bg=Tks.bgc)

    def button_set_true(self, event) -> None:
        self.hi_var.set(f"True")
        update_svar = self.hi_var.get()
        update_json("hearing_impaired", update_svar)

    def button_set_false(self, event) -> None:
        self.hi_var.set(f"False")
        update_svar = self.hi_var.get().split(" ")[0]
        update_json("hearing_impaired", update_svar)

    def button_set_both(self, event) -> None:
        self.hi_var.set(f"Both")
        update_svar = self.hi_var.get().split(" ")[0]
        update_json("hearing_impaired", update_svar)


class SearchThreshold(tk.Frame):
    def __init__(self, parent) -> None:
        tk.Frame.__init__(self, parent)
        pct_var = tk.StringVar()
        pct_var.set(f"{precentage} %")
        self._add = precentage
        self.pct_var = pct_var
        for i in range(1, 4):
            Draw.label(self, text=Tks.column_lenght50, row=1, col=i, font=Tks.font8)
        Draw.label(self, text="Search threshold", sticky="w", row=1, col=1, font=Tks.font8b)
        Draw.label(self, textvar=self.pct_var, row=1, col=2, font=Tks.font8b)
        Draw.button(self, text="+", row=1, col=3, sticky="e", bind_to=self.button_add_5, show_tip=True, text_tip="Add 5% to the search threshold\n A higher value means less chance of finding subtitles that are not synced witht the movie/series")
        Draw.button(self, text="-", row=1, col=3, sticky="w", bind_to=self.button_sub_5, show_tip=True, text_tip="Subtract 5% from the search threshold\n A lower value means more subtitles will be found and downloaded")
        self.configure(bg=Tks.bgc)

    def button_add_5(self, event) -> None:
        self._add += 5 if self._add < 100 else 0
        self.pct_var.set(f"{self._add} %")
        update_svar = int(self.pct_var.get().split(" ")[0])
        update_json("precentage_pass", update_svar)

    def button_sub_5(self, event) -> None:
        self._add -= 5 if self._add > 0 else 0
        self.pct_var.set(f"{self._add} %")
        update_svar = int(self.pct_var.get().split(" ")[0])
        update_json("precentage_pass", update_svar)


class ShowContextMenu(tk.Frame):
    def __init__(self, parent) -> None:
        tk.Frame.__init__(self, parent)
        context_menu = tk.StringVar()
        context_menu.set(f"True")
        self.context_menu = context_menu
        for i in range(1, 4):
            Draw.label(self, text=Tks.column_lenght50, row=1, col=i, font=Tks.font8)
        Draw.label(self, text="Show context menu", row=1, col=1, sticky="w", font=Tks.font8b)
        Draw.label(self, textvar=self.context_menu, row=1, col=2, font=Tks.font8b, anchor="center")
        Draw.button(self, text="True", row=1, col=3, sticky="e", bind_to=self.button_set_true, show_tip=True, text_tip="Add SubSearch to the context menu when you right click inside a folder")
        Draw.button(self, text="False", row=1, col=3, sticky="w", bind_to=self.button_set_false, show_tip=True, text_tip="Remove SubSearch from the context menu\n Used to 'uninstall' SubSearch")
        self.configure(bg=Tks.bgc)

    def button_set_true(self, event) -> None:
        self.context_menu.set(f"True")
        from src.utilities import edit_registry

        edit_registry.restore_context_menu()

    def button_set_false(self, event) -> None:
        self.context_menu.set(f"False")
        from src.utilities import edit_registry

        edit_registry.remove_context_menu()


class ShowContextMenuIcon(tk.Frame):
    def __init__(self, parent) -> None:
        tk.Frame.__init__(self, parent)
        cmi_var = tk.StringVar()
        cmi_var.set(f"{cm_icon}")
        self.cmi_var = cmi_var
        for i in range(1, 4):
            Draw.label(self, text=Tks.column_lenght50, row=1, col=i, font=Tks.font8)
        Draw.label(self, text="Show context menu icon", row=1, col=1, sticky="w", font=Tks.font8b)
        Draw.label(self, textvar=self.cmi_var, row=1, col=2, font=Tks.font8b)
        Draw.button(self, text="True", row=1, col=3, sticky="e", bind_to=self.button_set_true, show_tip=True, text_tip="Add a icon next to SubSearch in the context menu")
        Draw.button(self, text="False", row=1, col=3, sticky="w", bind_to=self.button_set_false, show_tip=True, text_tip="Remove the icon next to SubSearch in the context menu")
        self.configure(bg=Tks.bgc)

    def button_set_true(self, event) -> None:
        self.cmi_var.set(f"True")
        update_svar = self.cmi_var.get()
        update_json("context_menu_icon", update_svar)
        from src.utilities import edit_registry

        edit_registry.context_menu_icon()

    def button_set_false(self, event) -> None:
        self.cmi_var.set(f"False")
        update_svar = self.cmi_var.get()
        update_json("context_menu_icon", update_svar)
        from src.utilities import edit_registry

        edit_registry.context_menu_icon()


class ShowTerminalOnSearch(tk.Frame):
    def __init__(self, parent) -> None:
        tk.Frame.__init__(self, parent)
        terminal_var = tk.StringVar()
        terminal_var.set(f"{terminal_focus}")
        self.terminal_var = terminal_var
        for i in range(1, 4):
            Draw.label(self, text=Tks.column_lenght50, row=1, col=i, font=Tks.font8)
        Draw.label(self, text="Show terminal on search", row=1, col=1, sticky="w", font=Tks.font8b)
        Draw.label(self, textvar=self.terminal_var, row=1, col=2, font=Tks.font8b)
        Draw.button(self, text="True", row=1, col=3, sticky="e", bind_to=self.button_set_true, show_tip=True, text_tip="Show the terminal when searching for subtitles\n Everything shown in the terminal is avalible in search.log")
        Draw.button(self, text="False", row=1, col=3, sticky="w", bind_to=self.button_set_false, show_tip=True, text_tip="Hide the terminal when searching for subtitles")
        self.configure(bg=Tks.bgc)

    def button_set_true(self, event) -> None:
        self.terminal_var.set(f"True")
        update_svar = self.terminal_var.get()
        update_json("terminal_focus", update_svar)
        edit_registry.write_command_subkey()

    def button_set_false(self, event) -> None:
        self.terminal_var.set(f"False")
        update_svar = self.terminal_var.get()
        update_json("terminal_focus", update_svar)
        edit_registry.write_command_subkey()


class CheckForUpdates(tk.Frame):
    def __init__(self, parent) -> None:
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

    def button_check(self, event) -> None:
        self.updates_var.set(f"Searching for updates...")
        current, latest = check_for_updates(fgui=True)
        if current == latest:
            self.updates_var.set(f"You are up to date!")
        if current != latest:
            self.updates_var.set(f"New version available!")
            Draw.button(self, text=f"Get v{latest}", row=1, col=3, height=2, width=18, bind_to=self.button_download)

    def button_download(self, event) -> None:
        webbrowser.open("https://github.com/vagabondHustler/SubSearch/releases")


class CustomTitleBar(tk.Frame):
    def __init__(self, parent) -> None:
        tk.Frame.__init__(self, parent)
        self.after(10, self.remove_titlebar, root)
        self.parent = parent
        self._offsetx = 0
        self._offsety = 0
        root.focus_force()
        root.overrideredirect(True)

        button = Draw.button(self, text="X", row=0, col=0, height=1, width=2, abgc="#cd2e3e", bgc_e="#a72633", bgc_l="#811e28", fg_e=Tks.fgc, font=Tks.font10b, pady=5, padx=5, bind_to=self.tk_exit_press)
        label = tk.Label(root, text=" SubSearch", height=2, bg=Tks.buttonc, fg=Tks.fgc, font=Tks.font10b, justify="left", anchor="w", width=Tks.window_width)
        label.place(bordermode="outside", x=0, y=0)
        label.lower()

        self.button = button
        self.label = label

        label.bind("<Button-1>", self.titlebar_press)
        label.bind("<B1-Motion>", self.titlebar_drag)

        self.configure(bg=Tks.buttonc)

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
        root.destroy()

    def tk_exit_press(self, event) -> None:
        self.button.bind("<ButtonRelease-1>", self.tk_exit_release)


def set_window_position(w=Tks.window_width, h=Tks.window_height):
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = int((ws / 2) - (w / 2))
    y = int((hs / 2) - (h / 2))
    value = f"{w}x{h}+{x}+{y}"
    return value


if is_admin():
    if got_key() is False:
        set_default_values()
        edit_registry.add_context_menu()

    c_verison = current_version()
    root = tk.Tk(className=f" SubSearch")
    icon_path = cwd() + r"\src\data\icon.ico"
    root.iconbitmap(icon_path)
    root.geometry(set_window_position())
    root.resizable(False, False)
    # root.attributes("-topmost", True, "-alpha", 1)
    root.wm_attributes("-transparentcolor", "#2a2d2f")
    root.configure(bg=Tks.bgc)

    CustomTitleBar(root).place(x=Tks.window_width - 2, y=2, bordermode="inside", anchor="ne")
    tk.Frame(root, bg=Tks.bgc).pack(anchor="center", expand=True)
    tk.Frame(root, bg=Tks.bgc).pack(anchor="center", expand=True)
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

elif got_key:
    run_as_admin()
    sys.exit()
