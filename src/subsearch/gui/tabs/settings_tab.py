import tkinter as tk
import webbrowser
from tkinter import ttk

from subsearch.data import GUI_DATA, __version__
from subsearch.gui import tkinter_utils
from subsearch.utils import io_json, updates


class FileExtensions(tk.Frame):
    def __init__(self, parent) -> None:
        tk.Frame.__init__(self, parent)
        self.configure(bg=GUI_DATA.colors.dark_grey)
        self.data = io_json.get_json_data()
        self.file_extensions = io_json.get_json_key("file_extensions")
        number_of_buttons = len(self.file_extensions.items())
        label = tk.Label(self, text="File extensions")
        label.configure(tkinter_utils.DEFAULT_LABEL_CONFIG)
        label.grid(tkinter_utils.DEFAULT_LABEL_GRID)
        self.rownum = 0
        self.colnum = 0
        self.checkbox_value = {}
        number_of_rows = 4

        for _i, (key, value) in zip(range(number_of_buttons), self.file_extensions.items()):
            self.rownum += 1
            if self.rownum > number_of_rows:
                self.rownum = 1
                self.colnum += 1

            valuevar = tk.BooleanVar()
            valuevar.set(value)
            btn = ttk.Checkbutton(self, text=key, onvalue=True, offvalue=False, variable=valuevar)
            btn.grid(row=self.rownum, column=self.colnum, pady=2)
            self.checkbox_value[btn] = key, valuevar
            btn.bind("<Enter>", self.enter_button)
        tkinter_utils.set_default_grid_size(self)

    def enter_button(self, event) -> None:
        btn = event.widget
        btn.bind("<ButtonPress-1>", self.press_button)

    def press_button(self, event) -> None:
        btn = event.widget
        btn.bind("<ButtonRelease-1>", self.toggle_ext)

    def toggle_ext(self, event) -> None:
        btn = event.widget
        key = self.checkbox_value[btn][0]
        value = self.checkbox_value[btn][1]
        if value.get() is True:
            self.data["file_extensions"][key] = False
        elif value.get() is False:
            self.data["file_extensions"][key] = True
        io_json.set_config(self.data)

        self.update_registry()

    def update_registry(self) -> None:
        from subsearch.utils import io_winreg

        io_winreg.write_all_valuex()


class ShowContextMenu(tkinter_utils.ToggleableFrameButton):
    """
    Inherits from the tk_tools.ToggleableFrameButton class and create toggleable button widget with different settings.

    Class corresponds to a specific setting in the configuration file and has a unique label, configuration key, and other optional attributes.
    """

    def __init__(self, parent) -> None:
        tkinter_utils.ToggleableFrameButton.__init__(self, parent, "Context menu", "context_menu", write_to_reg=True)


class ShowContextMenuIcon(tkinter_utils.ToggleableFrameButton):
    """
    Inherits from the tk_tools.ToggleableFrameButton class and create toggleable button widget with different settings.

    Class corresponds to a specific setting in the configuration file and has a unique label, configuration key, and other optional attributes.
    """

    def __init__(self, parent) -> None:
        tkinter_utils.ToggleableFrameButton.__init__(self, parent, "Context menu icon", "context_menu_icon")


class ShowDownloadWindow(tkinter_utils.ToggleableFrameButton):
    """
    Inherits from the tk_tools.ToggleableFrameButton class and create toggleable button widget with different settings.

    Class corresponds to a specific setting in the configuration file and has a unique label, configuration key, and other optional attributes.
    """

    def __init__(self, parent) -> None:
        tkinter_utils.ToggleableFrameButton.__init__(self, parent, "Download window", "manual_download_fail")


class ShowTerminalOnSearch(tkinter_utils.ToggleableFrameButton):
    """
    Inherits from the tk_tools.ToggleableFrameButton class and create toggleable button widget with different settings.

    Class corresponds to a specific setting in the configuration file and has a unique label, configuration key, and other optional attributes.
    """

    def __init__(self, parent) -> None:
        tkinter_utils.ToggleableFrameButton.__init__(self, parent, "Terminal on search", "show_terminal", show_if_exe=False)


class LogToFile(tkinter_utils.ToggleableFrameButton):
    """
    Inherits from the tk_tools.ToggleableFrameButton class and create toggleable button widget with different settings.

    Class corresponds to a specific setting in the configuration file and has a unique label, configuration key, and other optional attributes.
    """

    def __init__(self, parent) -> None:
        tkinter_utils.ToggleableFrameButton.__init__(self, parent, "Log to file", "log_to_file")


class UseThreading(tkinter_utils.ToggleableFrameButton):
    """
    Inherits from the tk_tools.ToggleableFrameButton class and create toggleable button widget with different settings.

    Class corresponds to a specific setting in the configuration file and has a unique label, configuration key, and other optional attributes.
    """

    def __init__(self, parent) -> None:
        tkinter_utils.ToggleableFrameButton.__init__(self, parent, "Use threading", "use_threading")


class MultipleAppInstances(tkinter_utils.ToggleableFrameButton):
    """
    Inherits from the tk_tools.ToggleableFrameButton class and create toggleable button widget with different settings.

    Class corresponds to a specific setting in the configuration file and has a unique label, configuration key, and other optional attributes.
    """

    def __init__(self, parent) -> None:
        tkinter_utils.ToggleableFrameButton.__init__(self, parent, "Multiple app instances", "multiple_app_instances")


class CheckForUpdates(tk.Frame):
    def __init__(self, parent) -> None:
        tk.Frame.__init__(self, parent)
        self.configure(bg=GUI_DATA.colors.dark_grey)
        self.string_var = tk.StringVar()
        self.string_var.set(f"")
        label = tk.Label(self, text=f"Version {__version__}")
        label.configure(tkinter_utils.DEFAULT_LABEL_CONFIG)
        label.grid(tkinter_utils.DEFAULT_LABEL_GRID)
        self.clabel = tk.Label(self, textvariable=self.string_var)
        self.clabel.configure(bg=GUI_DATA.colors.dark_grey, fg=GUI_DATA.colors.yellow, font=GUI_DATA.fonts.cas8b)
        self.clabel.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
        btn_check = ttk.Button(
            self,
            text="Check for updates",
            width=18,
        )
        btn_check.grid(row=0, column=3, pady=2)
        self.btn_download = ttk.Button(
            self,
            text="",
            width=18,
        )
        self.btn_download.grid(row=0, column=2, pady=2)
        btn_check.bind("<Enter>", self.enter_button)
        self.btn_download.bind("<Enter>", self.enter_button)
        tkinter_utils.set_default_grid_size(self)

    def enter_button(self, event) -> None:
        btn = event.widget
        if btn["text"] == "Check for updates":
            btn.bind("<ButtonRelease-1>", self.button_check)
        if btn["text"].startswith("Get"):
            btn.bind("<ButtonRelease-1>", self.button_download)

    def button_check(self, event) -> None:
        self.string_var.set(f"Looking...")
        new_repo_avail, repo_is_prerelease = updates.is_new_version_avail()
        latest_version = updates.get_latest_version()
        if new_repo_avail and repo_is_prerelease:
            if "-rc" in latest_version:
                self.string_var.set(f"Release candidate")
            elif "-alpha" in latest_version:
                self.string_var.set(f"Alpha release")
            elif "-beta" in latest_version:
                self.string_var.set(f"Beta release")
        elif new_repo_avail and repo_is_prerelease is False:
            self.string_var.set(f"Stable release")
        else:
            self.string_var.set(f"Up to date")

        if new_repo_avail:
            self.btn_download.configure(text=f"Get v{latest_version}")

    def button_download(self, event) -> None:
        webbrowser.open("https://github.com/vagabondHustler/SubSearch/releases")
