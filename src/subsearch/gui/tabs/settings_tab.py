import tkinter as tk
import webbrowser
from tkinter import ttk

from subsearch.data import __version__, gui
from subsearch.gui import gui_toolkit
from subsearch.utils import io_json, update


class FileExtensions(tk.Frame):
    def __init__(self, parent) -> None:
        tk.Frame.__init__(self, parent)
        self.configure(bg=gui.colors.dark_grey)
        self.data = io_json.get_json_data()
        self.file_extensions = io_json.get_json_key("file_extensions")
        number_of_buttons = len(self.file_extensions.items())
        label = tk.Label(self, text="File extensions")
        label.configure(gui_toolkit.DEFAULT_LABEL_CONFIG)
        label.grid(gui_toolkit.DEFAULT_LABEL_GRID)
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
        gui_toolkit.set_default_grid_size(self)

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
        io_json.set_json_data(self.data)

        self.update_registry()

    def update_registry(self) -> None:
        from subsearch.utils import io_winreg

        io_winreg.write_all_valuex()


class ShowContextMenu(gui_toolkit.ToggleableFrameButton):
    """
    Inherits from the tk_tools.ToggleableFrameButton class and create toggleable button widget with different settings.

    Class corresponds to a specific setting in the configuration file and has a unique label, configuration key, and other optional attributes.
    """

    def __init__(self, parent) -> None:
        gui_toolkit.ToggleableFrameButton.__init__(self, parent, "Context menu", "context_menu", write_to_reg=True)


class ShowContextMenuIcon(gui_toolkit.ToggleableFrameButton):
    """
    Inherits from the tk_tools.ToggleableFrameButton class and create toggleable button widget with different settings.

    Class corresponds to a specific setting in the configuration file and has a unique label, configuration key, and other optional attributes.
    """

    def __init__(self, parent) -> None:
        gui_toolkit.ToggleableFrameButton.__init__(self, parent, "Context menu icon", "context_menu_icon")


class ShowDownloadWindow(gui_toolkit.ToggleableFrameButton):
    """
    Inherits from the tk_tools.ToggleableFrameButton class and create toggleable button widget with different settings.

    Class corresponds to a specific setting in the configuration file and has a unique label, configuration key, and other optional attributes.
    """

    def __init__(self, parent) -> None:
        gui_toolkit.ToggleableFrameButton.__init__(self, parent, "Download window", "manual_download_fail")


class ShowTerminalOnSearch(gui_toolkit.ToggleableFrameButton):
    """
    Inherits from the tk_tools.ToggleableFrameButton class and create toggleable button widget with different settings.

    Class corresponds to a specific setting in the configuration file and has a unique label, configuration key, and other optional attributes.
    """

    def __init__(self, parent) -> None:
        gui_toolkit.ToggleableFrameButton.__init__(self, parent, "Terminal on search", "show_terminal", show_if_exe=False)


class LogToFile(gui_toolkit.ToggleableFrameButton):
    """
    Inherits from the tk_tools.ToggleableFrameButton class and create toggleable button widget with different settings.

    Class corresponds to a specific setting in the configuration file and has a unique label, configuration key, and other optional attributes.
    """

    def __init__(self, parent) -> None:
        gui_toolkit.ToggleableFrameButton.__init__(self, parent, "Log to file", "log_to_file")


class UseThreading(gui_toolkit.ToggleableFrameButton):
    """
    Inherits from the tk_tools.ToggleableFrameButton class and create toggleable button widget with different settings.

    Class corresponds to a specific setting in the configuration file and has a unique label, configuration key, and other optional attributes.
    """

    def __init__(self, parent) -> None:
        gui_toolkit.ToggleableFrameButton.__init__(self, parent, "Use threading", "use_threading")


class MultipleAppInstances(gui_toolkit.ToggleableFrameButton):
    """
    Inherits from the tk_tools.ToggleableFrameButton class and create toggleable button widget with different settings.

    Class corresponds to a specific setting in the configuration file and has a unique label, configuration key, and other optional attributes.
    """

    def __init__(self, parent) -> None:
        gui_toolkit.ToggleableFrameButton.__init__(self, parent, "Multiple app instances", "multiple_app_instances")


class CheckForUpdates(tk.Frame):
    def __init__(self, parent) -> None:
        tk.Frame.__init__(self, parent)
        self.configure(bg=gui.colors.dark_grey)
        self.latest_version = ""
        self.btn_search = ttk.Button(
            self,
            text="Search for updates",
            width=40,
        )
        self.btn_visit_release_page = ttk.Button(
            self,
            text="Open in webbrowser",
            width=40,
        )
        self.btn_search.grid(row=0, column=2, pady=2)
        self.btn_search.bind("<Enter>", self.enter_button)
        gui_toolkit.set_default_grid_size(self)

    def enter_button(self, event) -> None:
        btn = event.widget
        if btn == self.btn_search:
            btn.bind("<ButtonRelease-1>", self.search_button)

    def search_button(self, event) -> None:
        new_repo_avail, repo_is_prerelease = update.is_new_version_avail()
        self.latest_version = update.get_latest_version()
        if new_repo_avail:
            self.btn_search.destroy()
            self.btn_visit_release_page.grid(row=0, column=2, pady=2)
            self.btn_visit_release_page.bind("<ButtonRelease-1>", self.visit_repository_button)
        if not new_repo_avail:
            self.btn_search["text"] = f"Latest version already installed"

    def visit_repository_button(self, event) -> None:
        webbrowser.open(f"https://github.com/vagabondHustler/subsearch/releases")
