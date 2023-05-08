import tkinter as tk
from typing import Any

from subsearch.data import GUI_DATA, app_paths
from subsearch.data.data_objects import FormattedMetadata
from subsearch.gui import set_theme, tkinter_utils
from subsearch.gui.tabs import dowload_tab, language_tab, search_tab, settings_tab
from subsearch.utils import file_manager, io_json, io_winreg


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
        self.configure(bg=GUI_DATA.colors.mid_grey_black, width=GUI_DATA.size.root_width, height=82)
        relx_value = 0.0
        btn_kwargs: dict[str, Any] = dict(
            master=self, width=54, height=54, bg=GUI_DATA.colors.mid_grey_black, highlightthickness=0
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
            tkinter_utils.asset_tab(btn_widget, btn_key, "rest")

        tkinter_utils.set_default_grid_size(self)
        self.active_tab = active_tab
        self.activate_tabs()

    def activate_tabs(self) -> None:
        self.tabs[self.active_tab].place(x=GUI_DATA.pos.content_x, y=GUI_DATA.pos.content_y, anchor="center")
        tkinter_utils.asset_tab(self.buttons[self.active_tab], self.active_tab, "press")
        self.parent.title(f"Subsearch - {self.active_tab} tab")

    def release_tab(self, event) -> None:
        btn_key, _btn_widget = self.get_btn(self.buttons, event)
        self.active_tab = btn_key
        self.activate_tabs()
        self.deactivate_tabs()

    def press_tab(self, event) -> None:
        btn_key, btn_widget = self.get_btn(self.buttons, event, False)
        btn_widget.bind("<ButtonRelease>", self.release_tab)
        tkinter_utils.asset_tab(btn_widget, btn_key, "press", y=20)

    def deactivate_tabs(self) -> None:
        for btn_key, btn_widget in self.buttons.items():
            if self.active_tab == btn_key:
                continue
            self.tabs[btn_key].place(x=GUI_DATA.pos.content_hidden_x, y=GUI_DATA.pos.content_y, anchor="nw")
            tkinter_utils.asset_tab(btn_widget, btn_key, "rest")

    def enter_tab(self, event) -> None:
        _btn_key, btn_widget = self.get_btn(self.buttons, event)
        btn_widget.bind("<ButtonPress>", self.press_tab)

    def leave_tab(self, event) -> None:
        _btn_key, btn_value = self.get_btn(self.buttons, event)
        btn_value.unbind("<ButtonPress>")
        self.activate_tabs()
        self.deactivate_tabs()

    def get_btn(self, dict_, event_, equals=True):
        for btn_key, btn_widget in dict_.items():
            if event_.widget == btn_widget and equals:
                return btn_key, btn_widget
            if event_.widget == btn_widget and not equals:
                return btn_key, btn_widget


class TabLanguage(tk.Frame):
    def __init__(self, parent) -> None:
        tk.Frame.__init__(self, parent, width=GUI_DATA.size.root_width, height=GUI_DATA.size.root_height)
        self.configure(bg=GUI_DATA.colors.dark_grey)
        language_tab.SelectLanguage(self).pack(anchor="center", expand=True)


class TabSearch(tk.Frame):
    def __init__(self, parent) -> None:
        tk.Frame.__init__(self, parent, width=GUI_DATA.size.root_width, height=GUI_DATA.size.root_height)
        self.configure(bg=GUI_DATA.colors.dark_grey)
        search_tab.Providers(self).pack(anchor="center")
        tk.Frame(self, height=80, bg=GUI_DATA.colors.dark_grey).pack(anchor="center", expand=True)
        search_tab.SubtitleType(self).pack(anchor="center")
        search_tab.SearchThreshold(self).pack(anchor="center")
        search_tab.RenameBestMatch(self).pack(anchor="center")


class TabSettings(tk.Frame):
    def __init__(self, parent) -> None:
        tk.Frame.__init__(self, parent, width=GUI_DATA.size.root_width, height=GUI_DATA.size.root_height)
        self.configure(bg=GUI_DATA.colors.dark_grey)
        settings_tab.FileExtensions(self).pack(anchor="center")
        tk.Frame(self, height=80, bg=GUI_DATA.colors.dark_grey).pack(anchor="center", expand=True)
        settings_tab.ShowContextMenu(self).pack(anchor="center")
        settings_tab.ShowContextMenuIcon(self).pack(anchor="center")
        settings_tab.ShowDownloadWindow(self).pack(anchor="center")
        settings_tab.UseThreading(self).pack(anchor="center")
        settings_tab.MultipleAppInstances(self).pack(anchor="center")
        settings_tab.LogToFile(self).pack(anchor="center")
        if file_manager.running_from_exe() is False:
            settings_tab.ShowTerminalOnSearch(self).pack(anchor="center")
        tk.Frame(self, height=20, bg=GUI_DATA.colors.dark_grey).pack(anchor="center", expand=True)
        settings_tab.CheckForUpdates(self).pack(anchor="center")


class TabDownload(tk.Frame):
    def __init__(self, parent, formatted_data: list[FormattedMetadata]) -> None:
        tk.Frame.__init__(self, parent, width=GUI_DATA.size.root_width, height=GUI_DATA.size.root_height)
        self.configure(bg=GUI_DATA.colors.dark_grey)
        dowload_tab.DownloadList(self, formatted_data).pack(anchor="center")


def open_tab(active_tab: str, **kwargs) -> None:
    """
    Opens a new tab depending on the active_tab argument passed in.

    Args:
        active_tab (str): A string representing which tab to activate.
        **kwargs: Arbitrary keyword arguments that should contain "formatted_data",
                  a list of FormattedMetadata.

    Returns:
        None: This function does not return anything, it manipulates the GUI instead.
    """
    try:
        formatted_data: list[FormattedMetadata] = kwargs["formatted_data"]
    except KeyError:
        formatted_data = None  # type: ignore
    root = initalize_root()
    set_theme("dark")
    tkinter_utils.set_custom_btn_styles()
    tabs = {
        "language": TabLanguage(root),
        "search": TabSearch(root),
        "settings": TabSettings(root),
        "download": TabDownload(root, formatted_data),
    }
    footer = TabManager(root, tabs, active_tab.lower())
    footer.place(y=GUI_DATA.size.root_height - 82)
    root.mainloop()


def initalize_root():
    """
    Initializes the Tkinter root window with the name `"Subsearch"`, sets its background color to `GUI_DATA.colors.dark_grey`,
    adds an icon bitmap from `__paths__.icon`, configures the window geometry using `tkinter_utils.WindowPosition.set` and makes the window non-resizable.
    If `io_winreg.registry_key_exists()` is `False` and `raw_json.get_config_key("context_menu")` is `True`,
    the default JSON configuration is set using `raw_json.set_default_json()` and a context menu is added to the registry using `io_winreg.add_context_menu()`.

    Returns:
      An instance of Tk() class representing the main window of Subsearch application.
    """
    if io_winreg.registry_key_exists() is False and io_json.get_json_key("context_menu"):
        io_json.set_default_json()
        io_winreg.add_context_menu()
    root = tk.Tk(className=f"Subsearch")
    root.configure(background=GUI_DATA.colors.dark_grey)
    root.iconbitmap(app_paths.icon)
    root.geometry(tkinter_utils.WindowPosition.set(root))  # type: ignore
    root.resizable(False, False)
    return root
