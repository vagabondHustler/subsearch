import ctypes
import sys
import tkinter as tk
import webbrowser

import src.utilities.edit_registry as edit_registry
from src.gui.root import Create, Tks, main
from src.utilities.current_user import got_key, is_admin, is_exe_version, run_as_admin
from src.utilities.edit_config import set_default_values, update_json
from src.utilities.read_config_json import get
from src.utilities.updates import check_for_updates, is_new_version_available
from src.utilities.version import current_version

languages = get("languages")
language, lang_abbr = get("language")
hearing_impared = get("hearing_impaired")
pct = get("percentage")
terminal_focus = get("terminal_focus")
cm_icon = get("cm_icon")
dl_window = get("show_download_window")


# set which language of the subtitles  should be included in the search
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
        Create.label(self, textvar=self.lang_var, fg=Tks.blue, row=1, col=2, font=Tks.font8b)
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
        self.configure(bg=Tks.dark_grey)

    def button_set_lang(self, event) -> None:
        btn = event.widget
        self.lang_var.set(btn.cget("text"))
        update_svar = self.lang_var.get()
        update_json("language", update_svar)


# set HI, none-HI or both HI and none-HI subtitles should be included in the search
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
        Create.label(self, textvar=self.hi_var, fg=Tks.blue, row=1, col=2, font=Tks.font8b)
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
        self.configure(bg=Tks.dark_grey)

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


# set how closely the subtitle name should match the release name of the media file
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
        Create.label(self, textvar=self.pct_var, fg=Tks.blue, row=1, col=2, font=Tks.font8b)
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
        self.configure(bg=Tks.dark_grey)

    def button_add_5(self, event) -> None:
        self.pct += 5 if self.pct < 100 else 0
        self.pct_var.set(f"{self.pct} %")
        update_svar = int(self.pct_var.get().split(" ")[0])
        update_json("percentage_pass", update_svar)

    def button_sub_5(self, event) -> None:
        self.pct -= 5 if self.pct > 0 else 0
        self.pct_var.set(f"{self.pct} %")
        update_svar = int(self.pct_var.get().split(" ")[0])
        update_json("percentage_pass", update_svar)


# remove or restore the context menu option when right-clicking
class ShowContextMenu(tk.Frame):
    def __init__(self, parent) -> None:
        tk.Frame.__init__(self, parent)
        context_menu = tk.StringVar()
        context_menu.set(f"True")
        self.context_menu = context_menu
        for i in range(1, 4):
            Create.label(self, text=Tks.col58, row=1, col=i, font=Tks.font8)
        Create.label(self, text="Show context menu", row=1, col=1, sticky="w", font=Tks.font8b)
        Create.label(self, textvar=self.context_menu, fg=Tks.blue, row=1, col=2, font=Tks.font8b, anchor="center")
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
        self.configure(bg=Tks.dark_grey)

    def button_set_true(self, event) -> None:
        self.context_menu.set(f"True")
        from src.utilities import edit_registry

        edit_registry.restore_context_menu()

    def button_set_false(self, event) -> None:
        self.context_menu.set(f"False")
        from src.utilities import edit_registry

        edit_registry.remove_context_menu()


# remove or restore the icon next to the context menu option when right clicking
class ShowContextMenuIcon(tk.Frame):
    def __init__(self, parent) -> None:
        tk.Frame.__init__(self, parent)
        cmi_var = tk.StringVar()
        cmi_var.set(f"{cm_icon}")
        self.cmi_var = cmi_var
        for i in range(1, 4):
            Create.label(self, text=Tks.col58, row=1, col=i, font=Tks.font8)
        Create.label(self, text="Show context menu icon", row=1, col=1, sticky="w", font=Tks.font8b)
        Create.label(self, textvar=self.cmi_var, fg=Tks.blue, row=1, col=2, font=Tks.font8b)
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
        self.configure(bg=Tks.dark_grey)

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


# remove or restore the icon next to the context menu option when right clicking
class ShowDownloadWindow(tk.Frame):
    def __init__(self, parent) -> None:
        tk.Frame.__init__(self, parent)
        dlw_var = tk.StringVar()
        dlw_var.set(f"{dl_window}")
        self.dlw_var = dlw_var
        for i in range(1, 4):
            Create.label(self, text=Tks.col58, row=1, col=i, font=Tks.font8)
        Create.label(self, text="Show download window", row=1, col=1, sticky="w", font=Tks.font8b)
        Create.label(self, textvar=self.dlw_var, fg=Tks.blue, row=1, col=2, font=Tks.font8b)
        Create.button(
            self,
            text="True",
            row=1,
            col=3,
            sticky="e",
            bind_to=self.button_set_true,
            tip_show=True,
            tip_text="If no subtitles are found show a window with the disregarded subtitles with download buttons to each of them",
        )
        Create.button(
            self,
            text="False",
            row=1,
            col=3,
            sticky="w",
            bind_to=self.button_set_false,
            tip_show=True,
            tip_text="No window will be shown if no subtitles are found\n The list can be found in search.log",
        )
        self.configure(bg=Tks.dark_grey)

    def button_set_true(self, event) -> None:
        self.dlw_var.set(f"True")
        update_svar = self.dlw_var.get()
        update_json("show_download_window", update_svar)

    def button_set_false(self, event) -> None:
        self.dlw_var.set(f"False")
        update_svar = self.dlw_var.get()
        update_json("show_download_window", update_svar)


# show a terminal with what the code is doing while searching
class ShowTerminalOnSearch(tk.Frame):
    def __init__(self, parent) -> None:
        tk.Frame.__init__(self, parent)
        terminal_var = tk.StringVar()
        if is_exe_version():
            terminal_var.set(f"Disabled")
        else:
            terminal_var.set(f"{terminal_focus}")

        self.terminal_var = terminal_var
        for i in range(1, 4):
            Create.label(self, text=Tks.col58, row=1, col=i, font=Tks.font8)
        Create.label(self, text="Show terminal on search", row=1, col=1, sticky="w", font=Tks.font8b)
        Create.label(self, textvar=self.terminal_var, fg=Tks.blue, row=1, col=2, font=Tks.font8b)
        if is_exe_version() is False:
            Create.button(
                self,
                text="True",
                row=1,
                col=3,
                sticky="e",
                bind_to=self.button_set_true,
                tip_show=True,
                tip_text="Show the terminal when searching for subtitles\n Everything shown in the terminal is avalible in search.log",
            )
            Create.button(
                self,
                text="False",
                row=1,
                col=3,
                sticky="w",
                bind_to=self.button_set_false,
                tip_show=True,
                tip_text="Hide the terminal when searching for subtitles",
            )
        self.configure(bg=Tks.dark_grey)

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


# check for new updates on the github repository
class CheckForUpdates(tk.Frame):
    def __init__(self, parent) -> None:
        tk.Frame.__init__(self, parent)
        updates_var = tk.StringVar()
        c_version = current_version()
        updates_var.set(f"")
        self.updates_var = updates_var
        for i in range(1, 4):
            Create.label(self, text=Tks.col58, row=1, col=i, font=Tks.font8)
        Create.label(self, text=f"SubScene version {c_version}", row=1, col=1, sticky="w", font=Tks.font8b)
        Create.label(self, textvar=self.updates_var, fg=Tks.blue, row=1, col=2, font=Tks.font8b)
        Create.button(
            self,
            text="Check for updates",
            row=1,
            col=3,
            height=2,
            width=18,
            bind_to=self.button_check,
        )
        self.configure(bg=Tks.dark_grey)

    def button_check(self, event) -> None:
        self.updates_var.set(f"Searching for updates...")
        value, release_type = is_new_version_available()
        latest_version = check_for_updates()
        if value:
            self.updates_var.set(f"New version available!")
            Create.button(
                self,
                text=f"Get {latest_version}",
                row=1,
                col=3,
                height=2,
                width=18,
                bind_to=self.button_download,
            )

        if value is False and release_type is None:
            self.updates_var.set(f"You are up to date!")
        elif value is False and release_type != "newer":
            self.updates_var.set(f"New {release_type} update available")
        elif value is False and release_type == "newer":
            self.updates_var.set(f"Branch ahead of main branch")

    def button_download(self, event) -> None:
        webbrowser.open("https://github.com/vagabondHustler/SubSearch/releases")


# get the window position so it can be placed in the center of the screen
def set_window_position(w=Tks.window_width, h=Tks.window_height):
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = int((ws / 2) - (w / 2))
    y = int((hs / 2) - (h / 2))
    value = f"{w}x{h}+{x}+{y}"
    return value


# only runs if file is run as administrator
if is_admin():
    if "win" in sys.platform:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    if got_key() is False:
        set_default_values()
        edit_registry.add_context_menu()

    root = main()
    SelectLanguage(root).pack(anchor="center")
    tk.Frame(root, bg=Tks.dark_grey).pack(anchor="center", expand=True)
    HearingImparedSubs(root).pack(anchor="center")
    SearchThreshold(root).pack(anchor="center")
    tk.Frame(root, bg=Tks.dark_grey).pack(anchor="center", expand=True)
    ShowContextMenu(root).pack(anchor="center")
    ShowContextMenuIcon(root).pack(anchor="center")
    ShowDownloadWindow(root).pack(anchor="center")
    ShowTerminalOnSearch(root).pack(anchor="center")
    tk.Frame(root, bg=Tks.dark_grey).pack(anchor="center", expand=True)
    CheckForUpdates(root).pack(anchor="center")
    tk.Frame(root, bg=Tks.dark_grey).pack(anchor="center", expand=True)

    root.mainloop()
    sys.exit()

# re-runs the file as an administrator
elif got_key:
    run_as_admin()
    sys.exit()
