import ctypes
import sys
import tkinter as tk
import webbrowser

import src.utilities.edit_registry as edit_registry
from src.gui.widget_root import main
from src.gui.functions import Create, ColorPicker
from src.gui.data import Window, Color, Font, Misc
from src.utilities.current_user import got_key, is_exe_version
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
        self.string_var = tk.StringVar()
        self.string_var.set(f"{LANGUAGE}, {LANG_ABBR}")
        number_of_buttons = len(LANGUAGES)
        self.rowcount = 0
        self.colcount = 1
        for i in range(1, 4):
            Create.label(self, text=Misc.col58, row=1, col=i, font=Font.cas8)
        Create.label(self, text="Selected language", sticky="w", row=1, col=1, font=Font.cas8b)
        self.clabel = Create.label(self, textvar=self.string_var, fg=Color.yellow, row=1, col=2, font=Font.cas8b)
        for i in range(number_of_buttons):
            self.rowcount += 1
            if self.rowcount == 8:
                self.colcount += 1
                self.rowcount = 1
            Create.button(
                self,
                text=LANGUAGES[i],
                row=self.rowcount + 1,
                col=self.colcount,
                height=2,
                width=24,
                padx=2,
                bind_to=self.set_language,
            )
        Create.button(
            self,
            abgc=Color.light_black,
            bge=Color.light_black,
            fg=Color.light_black,
            fge=Color.light_black,
            row=self.rowcount + 2,
            col=self.colcount,
            height=2,
            width=24,
        )
        self.entry = tk.Entry(self, text="asdf", width=28, bd=0, font=Font.cas8b, justify="center")
        self.entry.insert(0, "🞂 Enter language here 🞀")
        self.entry.configure(bg=Color.light_black, fg=Color.purple, insertbackground=Color.purple)
        self.entry.grid(ipady=8, padx=2, pady=2, row=self.rowcount + 2, column=self.colcount)
        self.add_button = Create.button(
            self,
            text="Add",
            abgc=Color.purple,
            bge=Color.black,
            fg=Color.white_grey,
            fge=Color.purple,
            row=self.rowcount + 3,
            col=self.colcount,
            height=2,
            width=10,
            padx=5,
            sticky="w",
            bind_to=self.add_language,
        )

        self.see_other_langs = Create.button(
            self,
            text="∙ ∙ ∙",
            abgc=Color.purple,
            bge=Color.black,
            fg=Color.white_grey,
            fge=Color.purple,
            row=self.rowcount + 3,
            col=self.colcount,
            height=2,
            width=10,
            padx=5,
            sticky="e",
        )
        self.entry.bind("<Enter>", self.entry_enter)
        self.see_other_langs.bind("<Enter>", self.other_langs_window)
        self.entry.bind("<Return>", self.add_language)
        self.configure(bg=Color.dark_grey)

    # pop up window with list of other languages
    def other_langs_window(self, event):
        self.clear_entry()
        rows = len(OTHER_LANGUAGES) / 2
        cols = 2
        row_size_y = 20.16
        row_size_x = 113
        csx = round(cols * row_size_x)
        csy = round(rows * row_size_y)

        self.toplvl = tk.Toplevel(background=Color.light_black, borderwidth=0)
        self.toplvl.overrideredirect(True)

        self.frame = tk.Frame(self.toplvl, background=Color.dark_grey, width=csx, height=csy, borderwidth=0)
        self.frame.place(relx=0.5, rely=0.5, anchor="center")

        root_x = root.winfo_rootx() + Window.width + 10
        root_y = root.winfo_rooty() + 38
        self.toplvl.geometry(f"{csx}x{csy}+{root_x}+{root_y}")
        for num, i in zip(range(0, 50), OTHER_LANGUAGES):
            Create.label(
                self.frame,
                bg=Color.dark_grey,
                text=i,
                font=Font.cas8,
                row=num if num < 25 else num - 25,
                col=0 if num < 25 else 1,
                sticky="w",
                padx=0,
                pady=0,
            )
        self.see_other_langs.configure(fg=Color.purple)
        self.see_other_langs.bind("<Leave>", self.destroy_toplvl)

    def destroy_toplvl(self, event):
        self.fill_entry()
        self.see_other_langs.configure(fg=Color.white_grey)
        self.see_other_langs.bind("<Enter>", self.other_langs_window)
        self.toplvl.destroy()

    # entry functions
    def entry_enter(self, event):
        if self.entry.get() == "🞂 Enter language here 🞀" or self.entry.get() == "E.g: Czech, cs":
            self.clear_entry()
            self.entry.bind("<Leave>", self.entry_leave)

    def entry_leave(self, event):
        if self.entry.get() == "" or self.entry.get() == "E.g: Czech, cs":
            self.fill_entry()
            self.entry.bind("<Enter>", self.entry_enter)

    def clear_entry(self):
        self.entry.delete(0, "end")
        self.entry.insert(0, "")
        self.entry.configure(fg=Color.purple)

    def fill_entry(self):
        self.entry.delete(0, "end")
        self.entry.insert(0, "🞂 Enter language here 🞀")
        self.entry.configure(fg=Color.purple)

    # set language
    def set_language(self, event):
        btn = event.widget
        self.string_var.set(btn.cget("text"))
        update_svar = self.string_var.get()
        update_json("language", update_svar)

    # add language from entry
    def add_language(self, event):
        x = self.entry.get()
        for i in OTHER_LANGUAGES:
            if x == i:
                self.string_var.set(self.entry.get())
                self.entry.configure(fg=Color.white_grey)
                update_svar = self.string_var.get()
                update_json("language", update_svar)
                return
        self.entry.delete(0, "end")
        self.entry.insert(0, "E.g: Czech, cs")
        self.entry.configure(fg=Color.red)


# set HI, none-HI or both HI and none-HI subtitles should be included in the search
class HearingImparedSubs(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.string_var = tk.StringVar()
        self.string_var.set(f"{HEARING_IMPARED}")
        for i in range(1, 4):
            Create.label(self, text=Misc.col58, row=1, col=i, font=Font.cas8)
        Create.label(self, text="Hearing impaired subtitles", sticky="w", row=1, col=1, font=Font.cas8b, anchor="w")
        self.clabel = Create.label(self, textvar=self.string_var, fg=Color.blue, row=1, col=2, font=Font.cas8b)
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

        ColorPicker(self.string_var, self.clabel)
        self.configure(bg=Color.dark_grey)

    def button_set_true(self, event):
        self.string_var.set(f"True")
        ColorPicker(self.string_var, self.clabel)
        update_svar = self.string_var.get()
        update_json("hearing_impaired", update_svar)

    def button_set_false(self, event):
        self.string_var.set(f"False")
        ColorPicker(self.string_var, self.clabel)
        update_svar = self.string_var.get().split(" ")[0]
        update_json("hearing_impaired", update_svar)

    def button_set_both(self, event):
        self.string_var.set(f"Both")
        ColorPicker(self.string_var, self.clabel)
        update_svar = self.string_var.get().split(" ")[0]
        update_json("hearing_impaired", update_svar)


# set how closely the subtitle name should match the release name of the media file
class SearchThreshold(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.string_var = tk.StringVar()
        self.string_var.set(f"{PCT} %")
        self.pct = PCT
        for i in range(1, 4):
            Create.label(self, text=Misc.col58, row=1, col=i, font=Font.cas8)
        Create.label(self, text="Search threshold", sticky="w", row=1, col=1, font=Font.cas8b)
        self.clabel = Create.label(self, textvar=self.string_var, fg=Color.blue, row=1, col=2, font=Font.cas8b)
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
        ColorPicker(self.string_var, self.clabel, self.pct)
        self.configure(bg=Color.dark_grey)

    def button_add_5(self, event):
        self.pct += 5 if self.pct < 100 else 0
        self.string_var.set(f"{self.pct} %")

        ColorPicker(self.string_var, self.clabel, self.pct)
        update_svar = int(self.pct)
        update_json("percentage_pass", update_svar)

    def button_sub_5(self, event):
        self.pct -= 5 if self.pct > 0 else 0
        self.string_var.set(f"{self.pct} %")
        ColorPicker(self.string_var, self.clabel, self.pct)
        update_svar = int(self.pct)
        update_json("percentage_pass", update_svar)


# remove or restore the context menu option when right-clicking
class ShowContextMenu(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.string_var = tk.StringVar()
        self.string_var.set(f"True")
        for i in range(1, 4):
            Create.label(self, text=Misc.col58, row=1, col=i, font=Font.cas8)
        Create.label(self, text="Show context menu", row=1, col=1, sticky="w", font=Font.cas8b)
        self.clabel = Create.label(
            self, textvar=self.string_var, fg=Color.blue, row=1, col=2, font=Font.cas8b, anchor="center"
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
        ColorPicker(self.string_var, self.clabel)
        self.configure(bg=Color.dark_grey)

    def button_set_true(self, event):
        self.string_var.set(f"True")
        ColorPicker(self.string_var, self.clabel)
        from src.utilities import edit_registry

        edit_registry.restore_context_menu()

    def button_set_false(self, event):
        self.string_var.set(f"False")
        ColorPicker(self.string_var, self.clabel)
        from src.utilities import edit_registry

        edit_registry.remove_context_menu()


# remove or restore the icon next to the context menu option when right clicking
class ShowContextMenuIcon(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.string_var = tk.StringVar()
        self.string_var.set(f"{CM_ICON}")
        for i in range(1, 4):
            Create.label(self, text=Misc.col58, row=1, col=i, font=Font.cas8)
        Create.label(self, text="Show context menu icon", row=1, col=1, sticky="w", font=Font.cas8b)
        self.clabel = Create.label(self, textvar=self.string_var, fg=Color.blue, row=1, col=2, font=Font.cas8b)
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
        ColorPicker(self.string_var, self.clabel)
        self.configure(bg=Color.dark_grey)

    def button_set_true(self, event):
        self.string_var.set(f"True")
        update_svar = self.string_var.get()
        ColorPicker(self.string_var, self.clabel)
        update_json("context_menu_icon", update_svar)
        from src.utilities import edit_registry

        edit_registry.context_menu_icon()

    def button_set_false(self, event):
        self.string_var.set(f"False")
        update_svar = self.string_var.get()
        ColorPicker(self.string_var, self.clabel)
        update_json("context_menu_icon", update_svar)
        from src.utilities import edit_registry

        edit_registry.context_menu_icon()


# remove or restore the icon next to the context menu option when right clicking
class ShowDownloadWindow(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.string_var = tk.StringVar()
        self.string_var.set(f"{DL_WINDOW}")
        for i in range(1, 4):
            Create.label(self, text=Misc.col58, row=1, col=i, font=Font.cas8)
        Create.label(self, text="Show download window", row=1, col=1, sticky="w", font=Font.cas8b)
        self.clabel = Create.label(self, textvar=self.string_var, fg=Color.blue, row=1, col=2, font=Font.cas8b)
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
        ColorPicker(self.string_var, self.clabel)
        self.configure(bg=Color.dark_grey)

    def button_set_true(self, event):
        self.string_var.set(f"True")
        ColorPicker(self.string_var, self.clabel)
        update_svar = self.string_var.get()
        update_json("show_download_window", update_svar)

    def button_set_false(self, event):
        self.string_var.set(f"False")
        ColorPicker(self.string_var, self.clabel)
        update_svar = self.string_var.get()
        update_json("show_download_window", update_svar)


# show a terminal with what the code is doing while searching
class ShowTerminalOnSearch(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.string_var = tk.StringVar()

        self.string_var.set(f"{TERMINAL_FOCUS}")
        for i in range(1, 4):
            Create.label(self, text=Misc.col58, row=1, col=i, font=Font.cas8)
        Create.label(self, text="Show terminal on search", row=1, col=1, sticky="w", font=Font.cas8b)
        self.clabel = Create.label(self, textvar=self.string_var, fg=Color.blue, row=1, col=2, font=Font.cas8b)
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
        ColorPicker(self.string_var, self.clabel)
        self.configure(bg=Color.dark_grey)

    def button_set_true(self, event):
        self.string_var.set(f"True")
        update_svar = self.string_var.get()
        ColorPicker(self.string_var, self.clabel)
        update_json("terminal_focus", update_svar)
        edit_registry.write_command_subkey()

    def button_set_false(self, event):
        self.string_var.set(f"False")
        update_svar = self.string_var.get()
        ColorPicker(self.string_var, self.clabel)
        update_json("terminal_focus", update_svar)
        edit_registry.write_command_subkey()


# check for new updates on the github repository
class CheckForUpdates(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.string_var = tk.StringVar()
        self.version = current_version()
        self.string_var.set(f"")
        for i in range(1, 4):
            Create.label(self, text=Misc.col58, row=1, col=i, font=Font.cas8)
        Create.label(self, text=f"SubScene version {self.version}", row=1, col=1, sticky="w", font=Font.cas8b)
        Create.label(self, textvar=self.string_var, fg=Color.blue, row=1, col=2, font=Font.cas8b)
        Create.button(
            self, text="Check for updates", row=1, col=3, height=2, width=18, fge=Color.green, bind_to=self.button_check
        )
        self.configure(bg=Color.dark_grey)

    def button_check(self, event):
        self.string_var.set(f"Searching for updates...")
        value, release_type = is_new_version_available()
        latest_version = check_for_updates()
        if value:
            self.string_var.set(f"New version available!")
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
            self.string_var.set(f"You are up to date!")
        elif value is False and release_type != "newer":
            self.string_var.set(f"New {release_type} update available")
        elif value is False and release_type == "newer":
            self.string_var.set(f"Branch ahead of main branch")

    def button_download(self, event):
        webbrowser.open("https://github.com/vagabondHustler/SubSearch/releases")


# get the window position so it can be placed in the center of the screen
def set_window_position(width: int = Window.width, height: int = Window.height):
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = int((ws / 2) - (width / 2))
    y = int((hs / 2) - (height / 2))
    value = f"{width}x{height}+{x}+{y}"
    return value


if got_key() is False:
    set_default_values()
    edit_registry.add_context_menu()

root = main()
SelectLanguage(root).pack(anchor="center")
tk.Frame(root, bg=Color.dark_grey).pack(anchor="center", expand=True)
HearingImparedSubs(root).pack(anchor="center")
SearchThreshold(root).pack(anchor="center")
tk.Frame(root, bg=Color.dark_grey).pack(anchor="center", expand=True)
ShowContextMenu(root).pack(anchor="center")
ShowContextMenuIcon(root).pack(anchor="center")
ShowDownloadWindow(root).pack(anchor="center")
if is_exe_version() is False:
    ShowTerminalOnSearch(root).pack(anchor="center")
tk.Frame(root, bg=Color.dark_grey).pack(anchor="center", expand=True)
CheckForUpdates(root).pack(anchor="center")
tk.Frame(root, bg=Color.dark_grey).pack(anchor="center", expand=True)


root.mainloop()
sys.exit()
