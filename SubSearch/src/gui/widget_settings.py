import tkinter as tk
import webbrowser

from src.gui import tkinter_data as tkd
from src.gui import tools, widget_root
from src.utilities import (
    current_user,
    edit_config,
    edit_registry,
    read_config_json,
    updates,
    version,
)


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
            tools.Create.label(self, text=tkd.Misc.col58, row=1, col=i, font=tkd.Font.cas8)
        tools.Create.label(self, text="Selected language", sticky="w", row=1, col=1, font=tkd.Font.cas8b)
        self.clabel = tools.Create.label(
            self, textvar=self.string_var, fg=tkd.Color.yellow, row=1, col=2, font=tkd.Font.cas8b
        )
        for i in range(number_of_buttons):
            self.rowcount += 1
            if self.rowcount == 8:
                self.colcount += 1
                self.rowcount = 1
            tools.Create.button(
                self,
                text=LANGUAGES[i],
                row=self.rowcount + 1,
                col=self.colcount,
                height=2,
                width=24,
                padx=2,
                bind_to=self.set_language,
            )
        tools.Create.button(
            self,
            abgc=tkd.Color.light_black,
            bge=tkd.Color.light_black,
            fg=tkd.Color.light_black,
            fge=tkd.Color.light_black,
            row=self.rowcount + 2,
            col=self.colcount,
            height=2,
            width=24,
        )
        self.entry = tk.Entry(self, text="asdf", width=28, bd=0, font=tkd.Font.cas8b, justify="center")
        self.entry.insert(0, "🞂 Enter language here 🞀")
        self.entry.configure(bg=tkd.Color.light_black, fg=tkd.Color.purple, insertbackground=tkd.Color.purple)
        self.entry.grid(ipady=8, padx=2, pady=2, row=self.rowcount + 2, column=self.colcount)
        self.add_button = tools.Create.button(
            self,
            text="Add",
            abgc=tkd.Color.purple,
            bge=tkd.Color.black,
            fg=tkd.Color.white_grey,
            fge=tkd.Color.purple,
            row=self.rowcount + 3,
            col=self.colcount,
            height=2,
            width=10,
            padx=5,
            sticky="w",
            bind_to=self.add_language,
        )

        self.see_other_langs = tools.Create.button(
            self,
            text="∙ ∙ ∙",
            abgc=tkd.Color.purple,
            bge=tkd.Color.black,
            fg=tkd.Color.white_grey,
            fge=tkd.Color.purple,
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
        self.configure(bg=tkd.Color.dark_grey)

    # pop up window with list of other languages
    def other_langs_window(self, event):
        self.clear_entry()
        rows = len(OTHER_LANGUAGES) / 2
        cols = 2
        row_size_y = 20.16
        row_size_x = 113
        csx = round(cols * row_size_x)
        csy = round(rows * row_size_y)

        self.toplvl = tk.Toplevel(background=tkd.Color.light_black, borderwidth=0)
        self.toplvl.overrideredirect(True)

        self.frame = tk.Frame(self.toplvl, background=tkd.Color.dark_grey, width=csx, height=csy, borderwidth=0)
        self.frame.place(relx=0.5, rely=0.5, anchor="center")

        root_x = root.winfo_rootx() + tkd.Window.width + 10
        root_y = root.winfo_rooty() + 37
        self.toplvl.geometry(f"{csx}x{csy}+{root_x}+{root_y}")
        for num, i in zip(range(0, 50), OTHER_LANGUAGES):
            tools.Create.label(
                self.frame,
                bg=tkd.Color.dark_grey,
                text=i,
                font=tkd.Font.cas8,
                row=num if num < 25 else num - 25,
                col=0 if num < 25 else 1,
                sticky="w",
                padx=0,
                pady=0,
            )
        self.see_other_langs.configure(fg=tkd.Color.purple)
        self.see_other_langs.bind("<Leave>", self.destroy_toplvl)

    def destroy_toplvl(self, event):
        self.fill_entry()
        self.see_other_langs.configure(fg=tkd.Color.white_grey)
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
        self.entry.configure(fg=tkd.Color.purple)

    def fill_entry(self):
        self.entry.delete(0, "end")
        self.entry.insert(0, "🞂 Enter language here 🞀")
        self.entry.configure(fg=tkd.Color.purple)

    # set language
    def set_language(self, event):
        btn = event.widget
        self.string_var.set(btn.cget("text"))
        update_svar = self.string_var.get()
        edit_config.update_json("language", update_svar)

    # add language from entry
    def add_language(self, event):
        x = self.entry.get()
        for i in OTHER_LANGUAGES:
            if x == i:
                self.string_var.set(self.entry.get())
                self.entry.configure(fg=tkd.Color.white_grey)
                update_svar = self.string_var.get()
                edit_config.update_json("language", update_svar)
                return
        self.entry.delete(0, "end")
        self.entry.insert(0, "E.g: Czech, cs")
        self.entry.configure(fg=tkd.Color.red)


# set HI, none-HI or both HI and none-HI subtitles should be included in the search
class HearingImparedSubs(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.string_var = tk.StringVar()
        self.string_var.set(f"{HEARING_IMPARED}")
        for i in range(1, 4):
            tools.Create.label(self, text=tkd.Misc.col58, row=1, col=i, font=tkd.Font.cas8)
        tools.Create.label(
            self, text="Hearing impaired subtitles", sticky="w", row=1, col=1, font=tkd.Font.cas8b, anchor="w"
        )
        self.clabel = tools.Create.label(
            self, textvar=self.string_var, fg=tkd.Color.blue, row=1, col=2, font=tkd.Font.cas8b
        )
        tools.Create.button(
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
        tools.Create.button(
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
        tools.Create.button(
            self,
            text="Both",
            row=1,
            col=3,
            width=7,
            bind_to=self.button_set_both,
            tip_show=True,
            tip_text="Use both hearing impaired and regular subtitles",
        )

        tools.ColorPicker(self.string_var, self.clabel)
        self.configure(bg=tkd.Color.dark_grey)

    def button_set_true(self, event):
        self.string_var.set(f"True")
        tools.ColorPicker(self.string_var, self.clabel)
        update_svar = self.string_var.get()
        edit_config.update_json("hearing_impaired", update_svar)

    def button_set_false(self, event):
        self.string_var.set(f"False")
        tools.ColorPicker(self.string_var, self.clabel)
        update_svar = self.string_var.get().split(" ")[0]
        edit_config.update_json("hearing_impaired", update_svar)

    def button_set_both(self, event):
        self.string_var.set(f"Both")
        tools.ColorPicker(self.string_var, self.clabel)
        update_svar = self.string_var.get().split(" ")[0]
        edit_config.update_json("hearing_impaired", update_svar)


# set how closely the subtitle name should match the release name of the media file
class SearchThreshold(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.string_var = tk.StringVar()
        self.string_var.set(f"{PCT} %")
        self.pct = PCT
        for i in range(1, 4):
            tools.Create.label(self, text=tkd.Misc.col58, row=1, col=i, font=tkd.Font.cas8)
        tools.Create.label(self, text="Search threshold", sticky="w", row=1, col=1, font=tkd.Font.cas8b)
        self.clabel = tools.Create.label(
            self, textvar=self.string_var, fg=tkd.Color.blue, row=1, col=2, font=tkd.Font.cas8b
        )
        tools.Create.button(
            self,
            text="+",
            row=1,
            col=3,
            sticky="e",
            bind_to=self.button_add_5,
            tip_show=True,
            tip_text="Add 5% to the search threshold\n A higher value means less chance of finding subtitles that are not synced witht the movie/series",
        )
        tools.Create.button(
            self,
            text="-",
            row=1,
            col=3,
            sticky="w",
            bind_to=self.button_sub_5,
            tip_show=True,
            tip_text="Subtract 5% from the search threshold\n A lower value means more subtitles will be found and downloaded",
        )
        tools.ColorPicker(self.string_var, self.clabel, self.pct)
        self.configure(bg=tkd.Color.dark_grey)

    def button_add_5(self, event):
        self.pct += 5 if self.pct < 100 else 0
        self.string_var.set(f"{self.pct} %")

        tools.ColorPicker(self.string_var, self.clabel, self.pct)
        update_svar = int(self.pct)
        edit_config.update_json("percentage_pass", update_svar)

    def button_sub_5(self, event):
        self.pct -= 5 if self.pct > 0 else 0
        self.string_var.set(f"{self.pct} %")
        tools.ColorPicker(self.string_var, self.clabel, self.pct)
        update_svar = int(self.pct)
        edit_config.update_json("percentage_pass", update_svar)


# remove or restore the context menu option when right-clicking
class ShowContextMenu(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.string_var = tk.StringVar()
        self.string_var.set(f"True")
        for i in range(1, 4):
            tools.Create.label(self, text=tkd.Misc.col58, row=1, col=i, font=tkd.Font.cas8)
        tools.Create.label(self, text="Show context menu", row=1, col=1, sticky="w", font=tkd.Font.cas8b)
        self.clabel = tools.Create.label(
            self, textvar=self.string_var, fg=tkd.Color.blue, row=1, col=2, font=tkd.Font.cas8b, anchor="center"
        )
        tools.Create.button(
            self,
            text="True",
            row=1,
            col=3,
            sticky="e",
            bind_to=self.button_set_true,
            tip_show=True,
            tip_text="Add SubSearch to the context menu when you right click inside a folder",
        )
        tools.Create.button(
            self,
            text="False",
            row=1,
            col=3,
            sticky="w",
            bind_to=self.button_set_false,
            tip_show=True,
            tip_text="Remove SubSearch from the context menu\n Used to 'uninstall' SubSearch",
        )
        tools.ColorPicker(self.string_var, self.clabel)
        self.configure(bg=tkd.Color.dark_grey)

    def button_set_true(self, event):
        self.string_var.set(f"True")
        tools.ColorPicker(self.string_var, self.clabel)
        from src.utilities import edit_registry

        edit_registry.restore_context_menu()

    def button_set_false(self, event):
        self.string_var.set(f"False")
        tools.ColorPicker(self.string_var, self.clabel)
        from src.utilities import edit_registry

        edit_registry.remove_context_menu()


# remove or restore the icon next to the context menu option when right clicking
class ShowContextMenuIcon(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.string_var = tk.StringVar()
        self.string_var.set(f"{CM_ICON}")
        for i in range(1, 4):
            tools.Create.label(self, text=tkd.Misc.col58, row=1, col=i, font=tkd.Font.cas8)
        tools.Create.label(self, text="Show context menu icon", row=1, col=1, sticky="w", font=tkd.Font.cas8b)
        self.clabel = tools.Create.label(
            self, textvar=self.string_var, fg=tkd.Color.blue, row=1, col=2, font=tkd.Font.cas8b
        )
        tools.Create.button(
            self,
            text="True",
            row=1,
            col=3,
            sticky="e",
            bind_to=self.button_set_true,
            tip_show=True,
            tip_text="Add a icon next to SubSearch in the context menu",
        )
        tools.Create.button(
            self,
            text="False",
            row=1,
            col=3,
            sticky="w",
            bind_to=self.button_set_false,
            tip_show=True,
            tip_text="Remove the icon next to SubSearch in the context menu",
        )
        tools.ColorPicker(self.string_var, self.clabel)
        self.configure(bg=tkd.Color.dark_grey)

    def button_set_true(self, event):
        self.string_var.set(f"True")
        update_svar = self.string_var.get()
        tools.ColorPicker(self.string_var, self.clabel)
        edit_config.update_json("context_menu_icon", update_svar)
        from src.utilities import edit_registry

        edit_registry.context_menu_icon()

    def button_set_false(self, event):
        self.string_var.set(f"False")
        update_svar = self.string_var.get()
        tools.ColorPicker(self.string_var, self.clabel)
        edit_config.update_json("context_menu_icon", update_svar)
        from src.utilities import edit_registry

        edit_registry.context_menu_icon()


# remove or restore the icon next to the context menu option when right clicking
class ShowDownloadWindow(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.string_var = tk.StringVar()
        self.string_var.set(f"{DL_WINDOW}")
        for i in range(1, 4):
            tools.Create.label(self, text=tkd.Misc.col58, row=1, col=i, font=tkd.Font.cas8)
        tools.Create.label(self, text="Show download window", row=1, col=1, sticky="w", font=tkd.Font.cas8b)
        self.clabel = tools.Create.label(
            self, textvar=self.string_var, fg=tkd.Color.blue, row=1, col=2, font=tkd.Font.cas8b
        )
        tools.Create.button(
            self,
            text="True",
            row=1,
            col=3,
            sticky="e",
            bind_to=self.button_set_true,
            tip_show=True,
            tip_text="If no subtitles are found show a window with the disregarded subtitles with download buttons to each of them",
        )
        tools.Create.button(
            self,
            text="False",
            row=1,
            col=3,
            sticky="w",
            bind_to=self.button_set_false,
            tip_show=True,
            tip_text="No window will be shown if no subtitles are found\n The list can be found in search.log",
        )
        tools.ColorPicker(self.string_var, self.clabel)
        self.configure(bg=tkd.Color.dark_grey)

    def button_set_true(self, event):
        self.string_var.set(f"True")
        tools.ColorPicker(self.string_var, self.clabel)
        update_svar = self.string_var.get()
        edit_config.update_json("show_download_window", update_svar)

    def button_set_false(self, event):
        self.string_var.set(f"False")
        tools.ColorPicker(self.string_var, self.clabel)
        update_svar = self.string_var.get()
        edit_config.update_json("show_download_window", update_svar)


# show a terminal with what the code is doing while searching
class ShowTerminalOnSearch(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.string_var = tk.StringVar()

        self.string_var.set(f"{TERMINAL_FOCUS}")
        for i in range(1, 4):
            tools.Create.label(self, text=tkd.Misc.col58, row=1, col=i, font=tkd.Font.cas8)
        tools.Create.label(self, text="Show terminal on search", row=1, col=1, sticky="w", font=tkd.Font.cas8b)
        self.clabel = tools.Create.label(
            self, textvar=self.string_var, fg=tkd.Color.blue, row=1, col=2, font=tkd.Font.cas8b
        )
        if current_user.is_exe() is False:
            tools.Create.button(
                self,
                text="True",
                row=1,
                col=3,
                sticky="e",
                bind_to=self.button_set_true,
                tip_show=True,
                tip_text="Show the terminal when searching for subtitles\n Everything shown in the terminal is avalible in search.log",
            )
            tools.Create.button(
                self,
                text="False",
                row=1,
                col=3,
                sticky="w",
                bind_to=self.button_set_false,
                tip_show=True,
                tip_text="Hide the terminal when searching for subtitles",
            )
        tools.ColorPicker(self.string_var, self.clabel)
        self.configure(bg=tkd.Color.dark_grey)

    def button_set_true(self, event):
        self.string_var.set(f"True")
        update_svar = self.string_var.get()
        tools.ColorPicker(self.string_var, self.clabel)
        edit_config.update_json("terminal_focus", update_svar)
        edit_registry.write_command_subkey()

    def button_set_false(self, event):
        self.string_var.set(f"False")
        update_svar = self.string_var.get()
        tools.ColorPicker(self.string_var, self.clabel)
        edit_config.update_json("terminal_focus", update_svar)
        edit_registry.write_command_subkey()


# check for new updates on the github repository
class CheckForUpdates(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.string_var = tk.StringVar()
        self.current_version = version.current()
        self.string_var.set(f"")
        for i in range(1, 4):
            tools.Create.label(self, text=tkd.Misc.col58, row=1, col=i, font=tkd.Font.cas8)
        tools.Create.label(
            self, text=f"SubScene version {self.current_version}", row=1, col=1, sticky="w", font=tkd.Font.cas8b
        )
        tools.Create.label(self, textvar=self.string_var, fg=tkd.Color.blue, row=1, col=2, font=tkd.Font.cas8b)
        tools.Create.button(
            self,
            text="Check for updates",
            row=1,
            col=3,
            height=2,
            width=18,
            fge=tkd.Color.green,
            bind_to=self.button_check,
        )
        self.configure(bg=tkd.Color.dark_grey)

    def button_check(self, event):
        self.string_var.set(f"Searching for updates...")
        value, release_type = updates.is_new_version_available()
        latest_version = updates.check_for_updates()
        if value:
            self.string_var.set(f"New version available!")
            tools.Create.button(
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


# # get the window position so it can be placed in the center of the screen
# def set_window_position(width: int = tkd.Window.width, height: int = tkd.Window.height):
#     ws = root.winfo_screenwidth()
#     hs = root.winfo_screenheight()
#     x = int((ws / 2) - (width / 2))
#     y = int((hs / 2) - (height / 2))
#     value = f"{width}x{height}+{x}+{y}"
#     return value

LANGUAGES = read_config_json.get("languages")
OTHER_LANGUAGES = read_config_json.get("other_languages")
LANGUAGE, LANG_ABBR = read_config_json.get("language")
HEARING_IMPARED = read_config_json.get("hearing_impaired")
PCT = read_config_json.get("percentage")
TERMINAL_FOCUS = read_config_json.get("terminal_focus")
CM_ICON = read_config_json.get("cm_icon")
DL_WINDOW = read_config_json.get("show_download_window")


def show_widget():
    global root
    if current_user.got_key() is False:
        edit_config.set_default_values()
        edit_registry.add_context_menu()

    root = widget_root.main()
    SelectLanguage(root).pack(anchor="center")
    tk.Frame(root, bg=tkd.Color.dark_grey).pack(anchor="center", expand=True)
    HearingImparedSubs(root).pack(anchor="center")
    SearchThreshold(root).pack(anchor="center")
    tk.Frame(root, bg=tkd.Color.dark_grey).pack(anchor="center", expand=True)
    ShowContextMenu(root).pack(anchor="center")
    ShowContextMenuIcon(root).pack(anchor="center")
    ShowDownloadWindow(root).pack(anchor="center")
    if current_user.is_exe() is False:
        ShowTerminalOnSearch(root).pack(anchor="center")
    tk.Frame(root, bg=tkd.Color.dark_grey).pack(anchor="center", expand=True)
    CheckForUpdates(root).pack(anchor="center")
    tk.Frame(root, bg=tkd.Color.dark_grey).pack(anchor="center", expand=True)

    root.mainloop()
