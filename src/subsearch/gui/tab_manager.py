import tkinter as tk
from typing import Any

from subsearch.data import __version__, gui
from subsearch.data.data_objects import PrettifiedDownloadData
from subsearch.gui import gui_toolkit, root
from subsearch.gui.tabs import dowload_tab, language_tab, search_tab, settings_tab
from subsearch.utils import file_manager


class TabManager(tk.Frame):
    """
    A class used to manage the tabs of a parent widget.

    Args:
        parent: The parent widget.
        tabs (dict[str, Any]): A dictionary containing tabs as a key-value pair. Key is the name of the tab and value is the content of the tab.
        active_tab (str): The current active tab.

    Attributes:
        parent: The parent widget.
        tabs (dict[str, Any]): A dictionary containing tabs as a key-value pair. Key is the name of the tab and value is the content of the tab.
        buttons: A dictionary containing button widgets as a key-value pair. Key is the name of the associated tab and value is the corresponding button widget.
        active_tab (str): The current active tab.

    Methods:
        activate_tabs(): Place the content of the active tab on the parent widget.
        release_tab(event): Called when a tab button is released. Set the active tab and call 'activate_tabs()' method.
        press_tab(event): Called when a tab button is pressed. Bind '<ButtonRelease>' event to the button widget.
        deactivate_tabs(): Hide the content of all tabs except the active one.
        enter_tab(event): Called when mouse enters a tab button. Bind '<ButtonPress>' event to the button widget.
        leave_tab(event):  Called when mouse leaves a tab button. Unbind '<ButtonPress>' event from the button widget, and call 'activate_tabs()' and 'deactivate_tabs()' methods.
        get_btn(dict_, event_, equals=True): Helper method to retrieve the button widget and its key.
    """

    def __init__(self, parent, tabs: dict[str, Any], active_tab: str) -> None:
        tk.Frame.__init__(self, parent)
        self.configure(bg=gui.colors.mid_grey_black, width=gui.size.root_width, height=82)
        relx_value = 0.0
        btn_kwargs: dict[str, Any] = dict(
            master=self, width=54, height=54, bg=gui.colors.mid_grey_black, highlightthickness=0
        )
        self.parent = parent
        self.tabs = tabs
        self.buttons = {}

        for tab_key in tabs.keys():
            self.buttons[tab_key] = tk.Canvas(**btn_kwargs)

        for btn_key, btn_widget in self.buttons.items():
            relx_value += 0.2
            btn_widget.place(relx=relx_value, rely=0.5, anchor="center")
            btn_widget.bind("<Enter>", self.enter_tab)
            btn_widget.bind("<Leave>", self.leave_tab)
            gui_toolkit.asset_tab(btn_widget, btn_key, "rest")

        gui_toolkit.set_default_grid_size(self)
        self.active_tab = active_tab
        self.activate_tabs()

    def activate_tabs(self) -> None:
        self.tabs[self.active_tab].place(x=gui.pos.content_x, y=gui.pos.content_y, anchor="center")
        gui_toolkit.asset_tab(self.buttons[self.active_tab], self.active_tab, "press")
        self.parent.title(f"Subsearch {__version__} - {self.active_tab.capitalize()} tab")

    def release_tab(self, event) -> None:
        btn_key, _btn_widget = self.get_btn(self.buttons, event)
        self.active_tab = btn_key
        self.activate_tabs()
        self.deactivate_tabs()

    def press_tab(self, event) -> None:
        btn_key, btn_widget = self.get_btn(self.buttons, event, False)
        btn_widget.bind("<ButtonRelease>", self.release_tab)
        gui_toolkit.asset_tab(btn_widget, btn_key, "press", y=20)

    def deactivate_tabs(self) -> None:
        for btn_key, btn_widget in self.buttons.items():
            if self.active_tab == btn_key:
                continue
            self.tabs[btn_key].place(x=gui.pos.content_hidden_x, y=gui.pos.content_y, anchor="nw")
            gui_toolkit.asset_tab(btn_widget, btn_key, "rest")

    def enter_tab(self, event) -> None:
        _btn_key, btn_widget = self.get_btn(self.buttons, event)
        btn_widget.bind("<ButtonPress>", self.press_tab)
        gui_toolkit.asset_tab(self.buttons[_btn_key], _btn_key, "hover")

    def leave_tab(self, event) -> None:
        _btn_key, btn_value = self.get_btn(self.buttons, event)
        btn_value.unbind("<ButtonPress>")
        gui_toolkit.asset_tab(self.buttons[_btn_key], _btn_key, "rest" if _btn_key != self.active_tab else "press")

    def get_btn(self, dict_, event_, equals=True):
        for btn_key, btn_widget in dict_.items():
            if event_.widget == btn_widget and equals:
                return btn_key, btn_widget
            if event_.widget == btn_widget and not equals:
                return btn_key, btn_widget


class TabLanguage(tk.Frame):
    def __init__(self, parent) -> None:
        tk.Frame.__init__(self, parent, width=gui.size.root_width, height=gui.size.root_height)
        self.configure(bg=gui.colors.dark_grey)
        language_tab.SelectLanguage(self).pack(anchor="center", expand=True)


class TabSearch(tk.Frame):
    def __init__(self, parent) -> None:
        tk.Frame.__init__(self, parent, width=gui.size.root_width, height=gui.size.root_height)
        self.configure(bg=gui.colors.dark_grey)
        search_tab.Providers(self).pack(anchor="center")
        tk.Frame(self, height=80, bg=gui.colors.dark_grey).pack(anchor="center", expand=True)
        search_tab.SubtitleType(self).pack(anchor="center")
        search_tab.SearchThreshold(self).pack(anchor="center")
        search_tab.ForeignOnly(self).pack(anchor="center")
        search_tab.RenameBestMatch(self).pack(anchor="center")


class TabSettings(tk.Frame):
    def __init__(self, parent) -> None:
        tk.Frame.__init__(self, parent, width=gui.size.root_width, height=gui.size.root_height)
        self.configure(bg=gui.colors.dark_grey)
        settings_tab.FileExtensions(self).pack(anchor="center")
        tk.Frame(self, height=80, bg=gui.colors.dark_grey).pack(anchor="center", expand=True)
        settings_tab.ShowContextMenu(self).pack(anchor="center")
        settings_tab.ShowContextMenuIcon(self).pack(anchor="center")
        settings_tab.ShowDownloadWindow(self).pack(anchor="center")
        settings_tab.UseThreading(self).pack(anchor="center")
        settings_tab.MultipleAppInstances(self).pack(anchor="center")
        settings_tab.LogToFile(self).pack(anchor="center")
        if file_manager.running_from_exe() is False:
            settings_tab.ShowTerminalOnSearch(self).pack(anchor="center")
        tk.Frame(self, height=20, bg=gui.colors.dark_grey).pack(anchor="center", expand=True)
        settings_tab.CheckForUpdates(self).pack(anchor="center")


class TabDownload(tk.Frame):
    def __init__(self, parent, formatted_data: list[PrettifiedDownloadData]) -> None:
        tk.Frame.__init__(self, parent, width=gui.size.root_width, height=gui.size.root_height)
        self.configure(bg=gui.colors.dark_grey)
        dowload_tab.DownloadList(self, formatted_data).pack(anchor="center")


def open_tab(active_tab: str, **kwargs) -> None:
    """
    Opens a new tab depending on the active_tab argument passed in.

    Args:
        active_tab (str): A string representing which tab to activate.

    Returns:
        None: This function does not return anything, it manipulates the GUI instead.
    """
    try:
        data: list[PrettifiedDownloadData] = kwargs["data"]
    except KeyError:
        data = []
    root
    gui_toolkit.configure_root(root)
    gui_toolkit.set_ttk_theme(root)
    gui_toolkit.set_custom_btn_styles()
    tabs = {
        "language": TabLanguage(root),
        "search": TabSearch(root),
        "settings": TabSettings(root),
        "download": TabDownload(root, data),
    }
    footer = TabManager(root, tabs, active_tab.lower())
    footer.place(y=gui.size.root_height - 82)
    root.mainloop()
