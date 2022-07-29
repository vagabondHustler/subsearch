import ctypes
import sys
import tkinter as tk
import webbrowser

import src.utilities.edit_registry as edit_registry
from src.gui.root import Tks, WindowPosition, Create, ColorPicker, main
from src.utilities.local_paths import root_directory
from src.utilities.current_user import got_key, is_admin, is_exe_version, run_as_admin
from src.utilities.edit_config import set_default_values, update_json
from src.utilities.read_config_json import get
from src.utilities.updates import check_for_updates, is_new_version_available
from src.utilities.version import current_version


LANGUAGES = get("languages")
OTHER_LANGUAGES = get("other_languages")
LANGUAGE, LANG_ABBR = get("language")
HEARING_IMPARED = get("hearing_impaired")
PCT = get("percentage")
TERMINAL_FOCUS = get("terminal_focus")
CM_ICON = get("cm_icon")
DL_WINDOW = get("show_download_window")


# set which language of the subtitles  should be included in the search
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
            Create.label(self, text=Tks.col58, row=1, col=i, font=Tks.font8)
        Create.label(self, text="Selected language", sticky="w", row=1, col=1, font=Tks.font8b)
        Create.label(self, textvar=self.lang_var, fg=Tks.purple, row=1, col=2, font=Tks.font8b)
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

    def button_set_lang(self, event):
        btn = event.widget
        self.lang_var.set(btn.cget("text"))
        update_svar = self.lang_var.get()
        update_json("language", update_svar)


# set HI, none-HI or both HI and none-HI subtitles should be included in the search
class HearingImparedSubs(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        string_var = tk.StringVar()
        string_var.set(f"{hearing_impared}")
        self.string_var = string_var
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
        self.clabel = Create.label(self, textvar=self.string_var, fg=Tks.blue, row=1, col=2, font=Tks.font8b)
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
        self.setting_label_color_picker()
        self.configure(bg=Tks.dark_grey)
    def setting_label_color_picker(self):
        if self.string_var.get() == "True":
            self.clabel.configure(fg=Tks.green)
        if self.string_var.get() == "False":
            self.clabel.configure(fg=Tks.red)
        if self.string_var.get() == "Both":
            self.clabel.configure(fg=Tks.blue)

    def button_set_true(self, event):
        self.string_var.set(f"True")
        self.setting_label_color_picker()
        update_svar = self.string_var.get()
        update_json("hearing_impaired", update_svar)

    def button_set_false(self, event):
        self.string_var.set(f"False")
        self.setting_label_color_picker()
        update_svar = self.string_var.get().split(" ")[0]
        update_json("hearing_impaired", update_svar)

    def button_set_both(self, event):
        self.string_var.set(f"Both")
        self.setting_label_color_picker()
        update_svar = self.string_var.get().split(" ")[0]
        update_json("hearing_impaired", update_svar)


# set how closely the subtitle name should match the release name of the media file
class SearchThreshold(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        string_var = tk.StringVar()
        string_var.set(f"{pct} %")
        self.pct = pct
        self.string_var = string_var
        for i in range(1, 4):
            Create.label(self, text=Tks.col58, row=1, col=i, font=Tks.font8)
        Create.label(self, text="Search threshold", sticky="w", row=1, col=1, font=Tks.font8b)
        self.clabel = Create.label(self, textvar=self.string_var, fg=Tks.blue, row=1, col=2, font=Tks.font8b)
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
        self.setting_label_color_picker()
        self.configure(bg=Tks.dark_grey)
    def setting_label_color_picker(self):
        if self.pct in range(75, 100):
            self.clabel.configure(fg=Tks.green)
        if self.pct in range(50, 75):
            self.clabel.configure(fg=Tks.green_brown)
        if self.pct in range(25, 50):
            self.clabel.configure(fg=Tks.red_brown)
        if self.pct in range(0, 25):
            self.clabel.configure(fg=Tks.red)

    def button_add_5(self, event):
        self.pct += 5 if self.pct < 100 else 0
        self.string_var.set(f"{self.pct} %")
        self.setting_label_color_picker()
        update_svar = int(self.string_var.get().split(" ")[0])
        update_json("percentage_pass", update_svar)

    def button_sub_5(self, event):
        self.pct -= 5 if self.pct > 0 else 0
        self.string_var.set(f"{self.pct} %")
        self.setting_label_color_picker()
        update_svar = int(self.string_var.get().split(" ")[0])
        update_json("percentage_pass", update_svar)


# remove or restore the context menu option when right-clicking
class ShowContextMenu(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        string_var = tk.StringVar()
        string_var.set(f"True")
        self.string_var = string_var
        for i in range(1, 4):
            Create.label(self, text=Tks.col58, row=1, col=i, font=Tks.font8)
        Create.label(self, text="Show context menu", row=1, col=1, sticky="w", font=Tks.font8b)
        self.clabel = Create.label(self, textvar=self.string_var, fg=Tks.blue, row=1, col=2, font=Tks.font8b, anchor="center")
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
        self.setting_label_color_picker()
        self.configure(bg=Tks.dark_grey)
    
    def setting_label_color_picker(self):
        if self.string_var.get() == "True":
            self.clabel.configure(fg=Tks.green)
        if self.string_var.get() == "False":
            self.clabel.configure(fg=Tks.red)
        if self.string_var.get() == "Both":
            self.clabel.configure(fg=Tks.blue)

    def button_set_true(self, event):
        self.string_var.set(f"True")
        self.setting_label_color_picker()
        from src.utilities import edit_registry

        edit_registry.restore_context_menu()

    def button_set_false(self, event):
        self.string_var.set(f"False")
        self.setting_label_color_picker()
        from src.utilities import edit_registry

        edit_registry.remove_context_menu()


# remove or restore the icon next to the context menu option when right clicking
class ShowContextMenuIcon(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        string_var = tk.StringVar()
        string_var.set(f"{cm_icon}")
        self.string_var = string_var
        for i in range(1, 4):
            Create.label(self, text=Tks.col58, row=1, col=i, font=Tks.font8)
        Create.label(self, text="Show context menu icon", row=1, col=1, sticky="w", font=Tks.font8b)
        self.clabel = Create.label(self, textvar=self.string_var, fg=Tks.blue, row=1, col=2, font=Tks.font8b)
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
        self.setting_label_color_picker()
        self.configure(bg=Tks.dark_grey)
        
    def setting_label_color_picker(self):
        if self.string_var.get() == "True":
            self.clabel.configure(fg=Tks.green)
        if self.string_var.get() == "False":
            self.clabel.configure(fg=Tks.red)

    def button_set_true(self, event):
        self.string_var.set(f"True")
        update_svar = self.string_var.get()
        self.setting_label_color_picker()
        update_json("context_menu_icon", update_svar)
        from src.utilities import edit_registry

        edit_registry.context_menu_icon()

    def button_set_false(self, event):
        self.string_var.set(f"False")
        update_svar = self.string_var.get()
        self.setting_label_color_picker()
        update_json("context_menu_icon", update_svar)
        from src.utilities import edit_registry

        edit_registry.context_menu_icon()


# remove or restore the icon next to the context menu option when right clicking
class ShowDownloadWindow(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        string_var = tk.StringVar()
        string_var.set(f"{dl_window}")
        self.string_var = string_var
        for i in range(1, 4):
            Create.label(self, text=Tks.col58, row=1, col=i, font=Tks.font8)
        Create.label(self, text="Show download window", row=1, col=1, sticky="w", font=Tks.font8b)
        self.clabel = Create.label(self, textvar=self.string_var, fg=Tks.blue, row=1, col=2, font=Tks.font8b)
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
        self.setting_label_color_picker()
        self.configure(bg=Tks.dark_grey)
        
    def setting_label_color_picker(self):
        if self.string_var.get() == "True":
            self.clabel.configure(fg=Tks.green)
        if self.string_var.get() == "False":
            self.clabel.configure(fg=Tks.red)

    def button_set_true(self, event):
        self.string_var.set(f"True")
        self.setting_label_color_picker()
        update_svar = self.string_var.get()
        update_json("show_download_window", update_svar)

    def button_set_false(self, event):
        self.string_var.set(f"False")
        self.setting_label_color_picker()
        update_svar = self.string_var.get()
        update_json("show_download_window", update_svar)


# show a terminal with what the code is doing while searching
class ShowTerminalOnSearch(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        string_var = tk.StringVar()
        if is_exe_version():
            string_var.set(f"Disabled")
        else:
            string_var.set(f"{terminal_focus}")

        self.string_var = string_var
        for i in range(1, 4):
            Create.label(self, text=Tks.col58, row=1, col=i, font=Tks.font8)
        Create.label(self, text="Show terminal on search", row=1, col=1, sticky="w", font=Tks.font8b)
        self.clabel = Create.label(self, textvar=self.string_var, fg=Tks.blue, row=1, col=2, font=Tks.font8b)
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
        self.setting_label_color_picker()
        self.configure(bg=Tks.dark_grey)
        
    def setting_label_color_picker(self):
        if self.string_var.get() == "True":
            self.clabel.configure(fg=Tks.green)
        if self.string_var.get() == "False":
            self.clabel.configure(fg=Tks.red)

    def button_set_true(self, event):
        if is_exe_version():
            return
        self.string_var.set(f"True")
        update_svar = self.string_var.get()
        self.setting_label_color_picker()
        update_json("terminal_focus", update_svar)
        edit_registry.write_command_subkey()

    def button_set_false(self, event):
        if is_exe_version():
            return
        self.string_var.set(f"False")
        update_svar = self.string_var.get()
        self.setting_label_color_picker()
        update_json("terminal_focus", update_svar)
        edit_registry.write_command_subkey()


# check for new updates on the github repository
class CheckForUpdates(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        string_label = tk.StringVar()
        c_version = current_version()
        string_label.set(f"")
        self.string_label = string_label
        for i in range(1, 4):
            Create.label(self, text=Tks.col58, row=1, col=i, font=Tks.font8)
        Create.label(self, text=f"SubScene version {c_version}", row=1, col=1, sticky="w", font=Tks.font8b)
        Create.label(self, textvar=self.string_label, fg=Tks.blue, row=1, col=2, font=Tks.font8b)
        Create.button(
            self,
            text="Check for updates",
            row=1,
            col=3,
            height=2,
            width=18,
            fge=Tks.green,
            bind_to=self.button_check,
        )
        self.configure(bg=Tks.dark_grey)


    def button_check(self, event):
        self.string_label.set(f"Searching for updates...")
        value, release_type = is_new_version_available()
        latest_version = check_for_updates()
        if value:
            self.string_label.set(f"New version available!")
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
            self.string_label.set(f"You are up to date!")
        elif value is False and release_type != "newer":
            self.string_label.set(f"New {release_type} update available")
        elif value is False and release_type == "newer":
            self.string_label.set(f"Branch ahead of main branch")

    def button_download(self, event):
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
