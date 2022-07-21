import ctypes
import sys
import tkinter as tk
import webbrowser
from dataclasses import dataclass

import src.utilities.edit_registry as edit_registry
from src.data._version import current_version
from src.gui.tooltip import Hovertip
from src.utilities.local_paths import cwd
from src.utilities.current_user import got_key, is_admin, run_as_admin, is_exe_version
from src.utilities.edit_config import set_default_values, update_json
from src.utilities.fetch_config import get
from src.utilities.updates import check_for_updates

languages = get("languages")
language, lang_abbr = get("language")
pct = get("percentage")
terminal_focus = get("terminal_focus")
hearing_impared = get("hearing_impaired")
cm_icon = get("cm_icon")


@dataclass
class Tks:
    window_width: int = 660
    window_height: int = 660
    bg: str = "#1b1d22"
    bgl: str = "#4c4c4c"
    fg: str = "#bdbdbd"
    fge: str = "#c5895e"
    bc: str = "#121417"
    abg: str = "#16181c"
    abg_disabled: str = "#303030"
    font8: str = "Cascadia 8"
    font8b: str = "Cascadia 8 bold"
    font10b: str = "Cascadia 10 bold"
    font20b: str = "Cascadia 20 bold"
    col58: str = " " * 58


class Create(tk.Frame):
    def __init__(self, parent) -> None:
        tk.Frame.__init__(self, parent)
        self.configure(bg=Tks.bg)

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
        root.destroy()

    def tk_exit_press(self, event) -> None:
        self.button.bind("<ButtonRelease-1>", self.tk_exit_release)


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
            Create.label(self, text=Tks.col58, row=1, col=i, font=Tks.font8)
        Create.label(self, text="Selected language", sticky="w", row=1, col=1, font=Tks.font8b)
        Create.label(self, textvar=self.lang_var, row=1, col=2, font=Tks.font8b)
        for i in range(number_of_buttons):
            rowcount += 1
            if rowcount == 8:
                colcount += 1
                rowcount = 1
            Create.button(
                self,
                text=languages[i],
                row=rowcount + 1,
                col=colcount,
                height=2,
                width=24,
                bind_to=self.button_set_lang,
            )
        self.configure(bg=Tks.bg)

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
            Create.label(self, text=Tks.col58, row=1, col=i, font=Tks.font8)
        Create.label(
            self,
            text="Hearing impaired subtitles",
            sticky="w",
            row=1,
            col=1,
            font=Tks.font8b,
            anchor="w",
        )
        Create.label(self, textvar=self.hi_var, row=1, col=2, font=Tks.font8b)
        Create.button(
            self,
            text="True",
            row=1,
            col=3,
            width=7,
            sticky="e",
            bind_to=self.button_set_true,
            tip_show=True,
            tip_text="Only use hearing impaired subtitles",
        )
        Create.button(
            self,
            text="False",
            row=1,
            col=3,
            width=7,
            sticky="w",
            bind_to=self.button_set_false,
            tip_show=True,
            tip_text="Only use regular subtitles",
        )
        Create.button(
            self,
            text="Both",
            row=1,
            col=3,
            width=7,
            bind_to=self.button_set_both,
            tip_show=True,
            tip_text="Use both hearing impaired and regular subtitles",
        )
        self.configure(bg=Tks.bg)

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
        pct_var.set(f"{pct} %")
        self.pct = pct
        self.pct_var = pct_var
        for i in range(1, 4):
            Create.label(self, text=Tks.col58, row=1, col=i, font=Tks.font8)
        Create.label(self, text="Search threshold", sticky="w", row=1, col=1, font=Tks.font8b)
        Create.label(self, textvar=self.pct_var, row=1, col=2, font=Tks.font8b)
        Create.button(
            self,
            text="+",
            row=1,
            col=3,
            sticky="e",
            bind_to=self.button_add_5,
            tip_show=True,
            tip_text="Add 5% to the search threshold\n A higher value means less chance of finding subtitles that are not synced witht the movie/series",
        )
        Create.button(
            self,
            text="-",
            row=1,
            col=3,
            sticky="w",
            bind_to=self.button_sub_5,
            tip_show=True,
            tip_text="Subtract 5% from the search threshold\n A lower value means more subtitles will be found and downloaded",
        )
        self.configure(bg=Tks.bg)

    def button_add_5(self, event) -> None:
        self.pct += 5 if self.pct < 100 else 0
        self.pct_var.set(f"{self.pct} %")
        update_svar = int(self.pct_var.get().split(" ")[0])
        update_json("precentage_pass", update_svar)

    def button_sub_5(self, event) -> None:
        self.pct -= 5 if self.pct > 0 else 0
        self.pct_var.set(f"{self.pct} %")
        update_svar = int(self.pct_var.get().split(" ")[0])
        update_json("precentage_pass", update_svar)


class ShowContextMenu(tk.Frame):
    def __init__(self, parent) -> None:
        tk.Frame.__init__(self, parent)
        context_menu = tk.StringVar()
        context_menu.set(f"True")
        self.context_menu = context_menu
        for i in range(1, 4):
            Create.label(self, text=Tks.col58, row=1, col=i, font=Tks.font8)
        Create.label(self, text="Show context menu", row=1, col=1, sticky="w", font=Tks.font8b)
        Create.label(
            self, textvar=self.context_menu, row=1, col=2, font=Tks.font8b, anchor="center"
        )
        Create.button(
            self,
            text="True",
            row=1,
            col=3,
            sticky="e",
            bind_to=self.button_set_true,
            tip_show=True,
            tip_text="Add SubSearch to the context menu when you right click inside a folder",
        )
        Create.button(
            self,
            text="False",
            row=1,
            col=3,
            sticky="w",
            bind_to=self.button_set_false,
            tip_show=True,
            tip_text="Remove SubSearch from the context menu\n Used to 'uninstall' SubSearch",
        )
        self.configure(bg=Tks.bg)

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
            Create.label(self, text=Tks.col58, row=1, col=i, font=Tks.font8)
        Create.label(
            self, text="Show context menu icon", row=1, col=1, sticky="w", font=Tks.font8b
        )
        Create.label(self, textvar=self.cmi_var, row=1, col=2, font=Tks.font8b)
        Create.button(
            self,
            text="True",
            row=1,
            col=3,
            sticky="e",
            bind_to=self.button_set_true,
            tip_show=True,
            tip_text="Add a icon next to SubSearch in the context menu",
        )
        Create.button(
            self,
            text="False",
            row=1,
            col=3,
            sticky="w",
            bind_to=self.button_set_false,
            tip_show=True,
            tip_text="Remove the icon next to SubSearch in the context menu",
        )
        self.configure(bg=Tks.bg)

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
        if is_exe_version():
            terminal_var.set(f"Disabled")
            text1 = " "
            text2 = text1
            tip_text1 = "Not available when running .exe-package"
            tip_text2 = tip_text1

        else:
            terminal_var.set(f"{terminal_focus}")
            text1 = "True"
            text2 = "False"
            tip_text1 = "Show the terminal when searching for subtitles\n Everything shown in the terminal is avalible in search.log"
            tip_text2 = "Hide the terminal when searching for subtitles"

        self.terminal_var = terminal_var
        for i in range(1, 4):
            Create.label(self, text=Tks.col58, row=1, col=i, font=Tks.font8)
        Create.label(
            self, text="Show terminal on search", row=1, col=1, sticky="w", font=Tks.font8b
        )
        Create.label(self, textvar=self.terminal_var, row=1, col=2, font=Tks.font8b)
        Create.button(
            self,
            text=text1,
            row=1,
            col=3,
            sticky="e",
            bind_to=self.button_set_true,
            tip_show=True,
            tip_text=tip_text1,
        )
        Create.button(
            self,
            text=text2,
            row=1,
            col=3,
            sticky="w",
            bind_to=self.button_set_false,
            tip_show=True,
            tip_text=tip_text2,
        )
        self.configure(bg=Tks.bg)

    def button_set_true(self, event) -> None:
        if is_exe_version():
            return
        self.terminal_var.set(f"True")
        update_svar = self.terminal_var.get()
        update_json("terminal_focus", update_svar)
        edit_registry.write_command_subkey()

    def button_set_false(self, event) -> None:
        if is_exe_version():
            return
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
            Create.label(self, text=Tks.col58, row=1, col=i, font=Tks.font8)
        Create.label(
            self, text=f"SubScene version {c_version}", row=1, col=1, sticky="w", font=Tks.font8b
        )
        Create.label(self, textvar=self.updates_var, row=1, col=2, font=Tks.font8b)
        Create.button(
            self,
            text="Check for updates",
            row=1,
            col=3,
            height=2,
            width=18,
            bind_to=self.button_check,
        )
        self.configure(bg=Tks.bg)

    def button_check(self, event) -> None:
        self.updates_var.set(f"Searching for updates...")
        current, latest = check_for_updates(fgui=True)
        if current == latest:
            self.updates_var.set(f"You are up to date!")
        if current != latest:
            self.updates_var.set(f"New version available!")
            Create.button(
                self,
                text=f"Get v{latest}",
                row=1,
                col=3,
                height=2,
                width=18,
                bind_to=self.button_download,
            )

    def button_download(self, event) -> None:
        webbrowser.open("https://github.com/vagabondHustler/SubSearch/releases")


def set_window_position(w=Tks.window_width, h=Tks.window_height):
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = int((ws / 2) - (w / 2))
    y = int((hs / 2) - (h / 2))
    value = f"{w}x{h}+{x}+{y}"
    return value


if is_admin():
    if "win" in sys.platform:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    if got_key() is False:
        set_default_values()
        edit_registry.add_context_menu()

    c_verison = current_version()
    root = tk.Tk(className=f" SubSearch")
    icon_path = cwd() + r"\src\data\64.ico"
    root.iconbitmap(icon_path)
    root.geometry(set_window_position())
    root.resizable(False, False)
    # root.attributes("-topmost", True, "-alpha", 1)
    root.wm_attributes("-transparentcolor", "#2a2d2f")
    root.configure(bg=Tks.bg)

    CustomTitleBar(root).place(x=Tks.window_width - 2, y=2, bordermode="inside", anchor="ne")
    tk.Frame(root, bg=Tks.bg).pack(anchor="center", expand=True)
    tk.Frame(root, bg=Tks.bg).pack(anchor="center", expand=True)
    tk.Frame(root, bg=Tks.bg).pack(anchor="center", expand=True)
    SelectLanguage(root).pack(anchor="center")
    tk.Frame(root, bg=Tks.bg).pack(anchor="center", expand=True)
    HearingImparedSubs(root).pack(anchor="center")
    SearchThreshold(root).pack(anchor="center")
    tk.Frame(root, bg=Tks.bg).pack(anchor="center", expand=True)
    ShowContextMenu(root).pack(anchor="center")
    ShowContextMenuIcon(root).pack(anchor="center")
    ShowTerminalOnSearch(root).pack(anchor="center")
    tk.Frame(root, bg=Tks.bg).pack(anchor="center", expand=True)
    CheckForUpdates(root).pack(anchor="center")
    tk.Frame(root, bg=Tks.bg).pack(anchor="center", expand=True)

    root.mainloop()

elif got_key:
    run_as_admin()
    sys.exit()
