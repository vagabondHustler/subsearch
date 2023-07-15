import tkinter as tk
from typing import Any

from subsearch.data import __version__, gui
from subsearch.data.data_objects import PrettifiedDownloadData
from subsearch.gui import gui_toolkit, root
from subsearch.gui.tabs import (
    download_manager,
    language_options,
    search_filters,
    subsearch_options,
)


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

    def __init__(self, parent, available_tabs: dict[str, Any], active_tab: str) -> None:
        tk.Frame.__init__(self, parent)
        self.configure(bg=gui.color.mid_grey_black, width=gui.size.width, height=82)
        relx_value = 0.0
        btn_kwargs: dict[str, Any] = dict(
            master=self, width=54, height=54, bg=gui.color.mid_grey_black, highlightthickness=0
        )
        self.parent = parent
        self.available_tabs = available_tabs
        self.buttons = {}

        for tab_key in available_tabs.keys():
            self.buttons[tab_key] = tk.Canvas(**btn_kwargs)

        for btn_key, btn_widget in self.buttons.items():
            relx_value += 0.2
            btn_widget.place(relx=relx_value, rely=0.5, anchor="center")
            btn_widget.bind("<Enter>", self.enter_menu_btn)
            btn_widget.bind("<Leave>", self.leave_menu_btn)
            gui_toolkit.asset_tab(btn_widget, btn_key, "rest")

        gui_toolkit.set_default_grid_size(self)
        self.active_tab = active_tab
        self.activate_tab()

    def activate_tab(self) -> None:
        self.available_tabs[self.active_tab].place(x=gui.pos.content_x, y=gui.pos.content_y, anchor="center")
        gui_toolkit.asset_tab(self.buttons[self.active_tab], self.active_tab, "press")
        title_tab = self.active_tab.capitalize().replace("_", " ")
        self.parent.title(f"Subsearch - {title_tab}")

    def release_tab(self, event) -> None:
        btn_key, _btn_widget = self.get_btn(self.buttons, event)
        self.active_tab = btn_key
        self.activate_tab()
        self.deactivate_tab()

    def deactivate_tab(self) -> None:
        for btn_key, btn_widget in self.buttons.items():
            if self.active_tab == btn_key:
                continue
            self.available_tabs[btn_key].place(x=gui.pos.content_hidden_x, y=gui.pos.content_y, anchor="nw")
            gui_toolkit.asset_tab(btn_widget, btn_key, "rest")

    def press_menu_btn(self, event) -> None:
        btn_key, btn_widget = self.get_btn(self.buttons, event, False)
        btn_widget.bind("<ButtonRelease>", self.release_tab)
        gui_toolkit.asset_tab(btn_widget, btn_key, "press", y=20)

    def enter_menu_btn(self, event) -> None:
        _btn_key, btn_widget = self.get_btn(self.buttons, event)
        btn_widget.bind("<ButtonPress>", self.press_menu_btn)
        gui_toolkit.asset_tab(self.buttons[_btn_key], _btn_key, "hover", y=23)

    def leave_menu_btn(self, event) -> None:
        _btn_key, btn_value = self.get_btn(self.buttons, event)
        btn_value.unbind("<ButtonPress>")
        gui_toolkit.asset_tab(self.buttons[_btn_key], _btn_key, "rest" if _btn_key != self.active_tab else "press")

    def get_btn(self, dict_, event_, equals=True):
        for btn_key, btn_widget in dict_.items():
            if event_.widget == btn_widget and equals:
                return btn_key, btn_widget
            if event_.widget == btn_widget and not equals:
                return btn_key, btn_widget


class LanguageOptions(tk.Frame):
    def __init__(self, parent) -> None:
        tk.Frame.__init__(self, parent, width=gui.size.width, height=gui.size.height)
        self.configure(bg=gui.color.dark_grey)
        language_options.SelectLanguage(self).pack(anchor="center", expand=True)


class SearchFilters(tk.Frame):
    def __init__(self, parent) -> None:
        tk.Frame.__init__(self, parent, width=gui.size.width, height=gui.size.height)
        self.configure(bg=gui.color.dark_grey)
        group_a = tk.Frame(self, bg=gui.color.dark_grey)
        group_a.pack(anchor="center", expand=True, fill="both")
        search_filters.Providers(group_a).pack(side=tk.RIGHT, anchor="center", expand=True, fill="both", padx=2)
        search_filters.SubtitleOptions(group_a).pack(side=tk.LEFT, anchor="center", expand=True, fill="both", padx=2)
        tk.Frame(self, height=80, bg=gui.color.dark_grey).pack(anchor="center", expand=True)
        search_filters.SearchThreshold(self).pack(anchor="center")


class SubsearchOptions(tk.Frame):
    def __init__(self, parent) -> None:
        tk.Frame.__init__(self, parent, width=gui.size.width, height=gui.size.height)
        self.configure(bg=gui.color.dark_grey)
        subsearch_options.FileExtensions(self).pack(anchor="center", fill="x")
        tk.Frame(self, height=40, bg=gui.color.dark_grey).pack(anchor="center", expand=True)
        subsearch_options.SubsearchOption(self).pack(anchor="center", fill="x")
        tk.Frame(self, height=80, bg=gui.color.dark_grey).pack(anchor="center", expand=True)
        subsearch_options.CheckForUpdates(self)


class DownloadManager(tk.Frame):
    def __init__(self, parent, formatted_data: list[PrettifiedDownloadData]) -> None:
        tk.Frame.__init__(self, parent, width=gui.size.width, height=gui.size.height)
        self.configure(bg=gui.color.dark_grey)
        download_manager.DownloadList(self, formatted_data).pack(anchor="center")


def open_tab(tab_name: str, **kwargs) -> None:
    """
    Opens a new tab depending on the tab_name argument passed in.

    Args:
        tab_name (str): A string representing which tab to activate.

    Returns:
        None: This function does not return anything, it manipulates the GUI instead.
    """

    data: list | list[PrettifiedDownloadData] = kwargs.get("data", [])
    gui_toolkit.configure_root(root)
    gui_toolkit.set_ttk_theme(root)
    gui_toolkit.set_custom_btn_styles()
    tabs = {
        "language_options": LanguageOptions(root),
        "search_filters": SearchFilters(root),
        "subsearch_options": SubsearchOptions(root),
        "download_manager": DownloadManager(root, data),
    }
    manager = TabManager(root, tabs, tab_name.lower())
    manager.place(y=gui.size.height - 82)
    root.mainloop()
