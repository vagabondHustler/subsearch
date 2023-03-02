import tkinter as tk
from tkinter import ttk
from typing import Any

from subsearch.data import GUI_DATA, __paths__
from subsearch.data.data_objects import FormattedMetadata
from subsearch.gui import (
    set_theme,
    tab_application_settings,
    tab_languages,
    tab_manual_download,
    tab_search_settings,
    tk_tools,
)
from subsearch.utils import file_manager, raw_config, raw_registry


class Footer(tk.Frame):
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
            tk_tools.asset_tab(btn_widget, btn_key, "rest")

        tk_tools.set_default_grid_size(self)
        self.active_tab = active_tab
        self.activate_tabs()

    def activate_tabs(self) -> None:
        self.tabs[self.active_tab].place(x=GUI_DATA.pos.content_x, y=GUI_DATA.pos.content_y, anchor="center")
        tk_tools.asset_tab(self.buttons[self.active_tab], self.active_tab, "press")
        self.parent.title(f"Subsearch - {self.active_tab} tab")

    def release_tab(self, event) -> None:
        btn_key, _btn_widget = self.get_btn(self.buttons, event)
        self.active_tab = btn_key
        self.activate_tabs()
        self.deactivate_tabs()

    def press_tab(self, event) -> None:
        btn_key, btn_widget = self.get_btn(self.buttons, event, False)
        btn_widget.bind("<ButtonRelease>", self.release_tab)
        tk_tools.asset_tab(btn_widget, btn_key, "press", y=20)

    def deactivate_tabs(self) -> None:
        for btn_key, btn_widget in self.buttons.items():
            if self.active_tab == btn_key:
                continue
            self.tabs[btn_key].place(x=GUI_DATA.pos.content_hidden_x, y=GUI_DATA.pos.content_y, anchor="nw")
            tk_tools.asset_tab(btn_widget, btn_key, "rest")

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
        tab_languages.SelectLanguage(self).pack(anchor="center", expand=True)


class TabSearch(tk.Frame):
    def __init__(self, parent) -> None:
        tk.Frame.__init__(self, parent, width=GUI_DATA.size.root_width, height=GUI_DATA.size.root_height)
        self.configure(bg=GUI_DATA.colors.dark_grey)
        tab_search_settings.Providers(self).pack(anchor="center")
        tk.Frame(self, height=80, bg=GUI_DATA.colors.dark_grey).pack(anchor="center", expand=True)
        tab_search_settings.SubtitleType(self).pack(anchor="center")
        tab_search_settings.SearchThreshold(self).pack(anchor="center")
        tab_search_settings.RenameBestMatch(self).pack(anchor="center")


class TabSettings(tk.Frame):
    def __init__(self, parent) -> None:
        tk.Frame.__init__(self, parent, width=GUI_DATA.size.root_width, height=GUI_DATA.size.root_height)
        self.configure(bg=GUI_DATA.colors.dark_grey)
        tab_application_settings.FileExtensions(self).pack(anchor="center")
        tk.Frame(self, height=80, bg=GUI_DATA.colors.dark_grey).pack(anchor="center", expand=True)
        tab_application_settings.ShowContextMenu(self).pack(anchor="center")
        tab_application_settings.ShowContextMenuIcon(self).pack(anchor="center")
        tab_application_settings.ShowDownloadWindow(self).pack(anchor="center")
        tab_application_settings.UseThreading(self).pack(anchor="center")
        tab_application_settings.LogToFile(self).pack(anchor="center")
        if file_manager.running_from_exe() is False:
            tab_application_settings.ShowTerminalOnSearch(self).pack(anchor="center")
        tk.Frame(self, height=20, bg=GUI_DATA.colors.dark_grey).pack(anchor="center", expand=True)
        tab_application_settings.CheckForUpdates(self).pack(anchor="center")


class TabDownload(tk.Frame):
    def __init__(self, parent, formatted_data: list[FormattedMetadata]) -> None:
        tk.Frame.__init__(self, parent, width=GUI_DATA.size.root_width, height=GUI_DATA.size.root_height)
        self.configure(bg=GUI_DATA.colors.dark_grey)
        tab_manual_download.DownloadList(self, formatted_data).pack(anchor="center")


def open_tab(active_tab: str, **kwargs) -> None:
    try:
        formatted_data: list[FormattedMetadata] = kwargs["formatted_data"]
    except KeyError:
        formatted_data = None  # type: ignore
    root = main()
    set_theme("dark")
    tk_tools.set_custom_btn_styles()
    tabs = {
        "language": TabLanguage(root),
        "search": TabSearch(root),
        "settings": TabSettings(root),
        "download": TabDownload(root, formatted_data),
    }
    footer = Footer(root, tabs, active_tab.lower())
    footer.place(y=GUI_DATA.size.root_height - 82)
    root.mainloop()


def main():
    if raw_registry.registry_key_exists() is False and raw_config.get_config_key("context_menu"):
        raw_config.set_default_json()
        raw_registry.add_context_menu()
    root = tk.Tk(className=f"Subsearch")
    root.configure(background=GUI_DATA.colors.dark_grey)
    root.iconbitmap(__paths__.icon)
    root.geometry(tk_tools.WindowPosition.set(root))
    root.resizable(False, False)
    return root
