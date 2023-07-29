import tkinter as tk
from typing import Any

from subsearch.data import __version__
from subsearch.data.data_classes import Subtitle
from subsearch.gui import resource_loader, root, utils
from subsearch.gui.resources import config as cfg
from subsearch.gui.screens import (
    download_manager,
    language_options,
    search_options,
    subsearch_options,
)


class ScreenManager(tk.Frame):
    """
    A class used to manage the screens of a parent widget.

    Args:
        parent: The parent widget.
        screens (dict[str, Any]): A dictionary containing screens as a key-value pair. Key is the name of the screen and value is the content of the screen.
        active_tab (str): The current active screen.

    Attributes:
        parent: The parent widget.
        screens (dict[str, Any]): A dictionary containing screens as a key-value pair. Key is the name of the screen and value is the content of the screen.
        buttons: A dictionary containing button widgets as a key-value pair. Key is the name of the associated screen and value is the corresponding button widget.
        active_tab (str): The current active screen.

    Methods:
        activate_screens(): Place the content of the active screen on the parent widget.
        release_tab(event): Called when a screen button is released. Set the active screen and call 'activate_screens()' method.
        press_tab(event): Called when a screen button is pressed. Bind '<ButtonRelease>' event to the button widget.
        deactivate_screens(): Hide the content of all screens except the active one.
        enter_tab(event): Called when mouse enters a screen button. Bind '<ButtonPress>' event to the button widget.
        leave_tab(event):  Called when mouse leaves a screen button. Unbind '<ButtonPress>' event from the button widget, and call 'activate_screens()' and 'deactivate_screens()' methods.
        get_btn(dict_, event_, equals=True): Helper method to retrieve the button widget and its key.
    """

    def __init__(self, parent, available_screens: dict[str, Any], active_screen: str) -> None:
        tk.Frame.__init__(self, parent)
        self.configure(bg=cfg.color.default_bg_dark, width=cfg.size.width, height=82)
        relx_value = 0.0
        btn_kwargs: dict[str, Any] = dict(
            master=self, width=54, height=54, bg=cfg.color.default_bg_dark, highlightthickness=0
        )
        self.parent = parent
        self.available_screens = available_screens
        self.buttons = {}

        for tab_key in available_screens.keys():
            self.buttons[tab_key] = tk.Canvas(**btn_kwargs)

        for btn_key, btn_widget in self.buttons.items():
            relx_value += 0.2
            btn_widget.place(relx=relx_value, rely=0.5, anchor="center")
            btn_widget.bind("<Enter>", self.enter_menu_btn)
            btn_widget.bind("<Leave>", self.leave_menu_btn)
            resource_loader.asset_menu_btn(btn_widget, btn_key, "rest")

        self.active_screen = active_screen
        self.activate_screen()

    def activate_screen(self) -> None:
        self.available_screens[self.active_screen].place(x=cfg.position.screen_x, y=cfg.position.screen_y, anchor="center")
        resource_loader.asset_menu_btn(self.buttons[self.active_screen], self.active_screen, "press")
        title_tab = self.active_screen.capitalize().replace("_", " ")
        self.parent.title(f"Subsearch - {title_tab}")

    def deactivate_screen(self) -> None:
        for btn_key, btn_widget in self.buttons.items():
            if self.active_screen == btn_key:
                continue
            self.available_screens[btn_key].place(x=cfg.position.screen_hidden_x, y=cfg.position.screen_y, anchor="nw")
            resource_loader.asset_menu_btn(btn_widget, btn_key, "rest")

    def enter_menu_btn(self, event) -> None:
        _btn_key, btn_widget = self.get_btn(self.buttons, event)
        btn_widget.bind("<ButtonPress>", self.press_menu_btn)
        resource_loader.asset_menu_btn(self.buttons[_btn_key], _btn_key, "hover", y=23)

    def leave_menu_btn(self, event) -> None:
        _btn_key, btn_value = self.get_btn(self.buttons, event)
        btn_value.unbind("<ButtonPress>")
        resource_loader.asset_menu_btn(
            self.buttons[_btn_key], _btn_key, "rest" if _btn_key != self.active_screen else "press"
        )

    def press_menu_btn(self, event) -> None:
        btn_key, btn_widget = self.get_btn(self.buttons, event, False)
        btn_widget.bind("<ButtonRelease>", self.release_menu_btn)
        resource_loader.asset_menu_btn(btn_widget, btn_key, "press", y=20)

    def release_menu_btn(self, event) -> None:
        btn_key, _btn_widget = self.get_btn(self.buttons, event)
        self.active_screen = btn_key
        self.activate_screen()
        self.deactivate_screen()

    def get_btn(self, btns: dict, event_: Any, equals=True):
        for btn_key, btn_widget in btns.items():
            if event_.widget == btn_widget and equals:
                return btn_key, btn_widget
            if event_.widget == btn_widget and not equals:
                return btn_key, btn_widget


class LanguageOptions(tk.Frame):
    def __init__(self, parent) -> None:
        tk.Frame.__init__(self, parent, width=cfg.size.width, height=cfg.size.height)
        self.configure(bg=cfg.color.default_bg)
        language_options.SelectLanguage(self).pack(anchor="center", expand=True)


class SearchOptions(tk.Frame):
    def __init__(self, parent) -> None:
        tk.Frame.__init__(self, parent, width=cfg.size.width, height=cfg.size.height)
        self.configure(bg=cfg.color.default_bg)
        group_a = tk.Frame(self, bg=cfg.color.default_bg)
        group_a.pack(anchor="center", expand=True, fill="both")
        search_options.SubtitleFilters(group_a).pack(side=tk.LEFT, anchor="center", expand=True, fill="both", padx=2)
        search_options.Providers(group_a).pack(side=tk.LEFT, anchor="center", expand=True, fill="both", padx=2)
        tk.Frame(self, height=30, bg=cfg.color.default_bg).pack(anchor="center", expand=True)
        search_options.SubtitlePostProcessing(self).pack(anchor="center", expand=True, fill="x")
        search_options.SubtitlePostProcessingDirectory(self).pack(anchor="center", expand=True, fill="x")
        tk.Frame(self, height=60, bg=cfg.color.default_bg).pack(anchor="center", expand=True)
        search_options.SearchThreshold(self).pack(anchor="center")


class SubsearchOptions(tk.Frame):
    def __init__(self, parent) -> None:
        tk.Frame.__init__(self, parent, width=cfg.size.width, height=cfg.size.height)
        self.configure(bg=cfg.color.default_bg)
        subsearch_options.FileExtensions(self).pack(anchor="center", fill="x")
        tk.Frame(self, height=40, bg=cfg.color.default_bg).pack(anchor="center", expand=True)
        subsearch_options.SubsearchOption(self).pack(anchor="center", fill="x")
        tk.Frame(self, height=80, bg=cfg.color.default_bg).pack(anchor="center", expand=True)
        subsearch_options.CheckForUpdates(self)


class DownloadManager(tk.Frame):
    def __init__(self, parent, subtitles: list[Subtitle]) -> None:
        tk.Frame.__init__(self, parent, width=cfg.size.width, height=cfg.size.height)
        self.configure(bg=cfg.color.default_bg)
        download_manager.DownloadManager(self, subtitles).pack(anchor="center")


def open_screen(tab_name: str, **kwargs) -> None:
    """
    Opens a new screen depending on the tab_name argument passed in.

    Args:
        tab_name (str): A string representing which screen to activate.

    Returns:
        None: This function does not return anything, it manipulates the GUI instead.
    """
    root.bind("<KeyPress>", close_mainloop)
    subtitles: list | list[Subtitle] = kwargs.get("subtitles", [])
    utils.configure_root(root)
    resource_loader.set_ttk_theme(root)
    screens = {
        "language_options": LanguageOptions(root),
        "search_options": SearchOptions(root),
        "subsearch_options": SubsearchOptions(root),
        "download_manager": DownloadManager(root, subtitles),
    }
    manager = ScreenManager(root, screens, tab_name.lower())
    manager.place(y=cfg.size.height - 82)
    root.mainloop()


def close_mainloop(event):
    if event.keysym == "Escape":
        root.quit()
