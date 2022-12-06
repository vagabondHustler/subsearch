import tkinter as tk
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
        self.parent = parent
        self.tabs = tabs
        self.button_language = tk.Canvas(
            self,
            width=54,
            height=54,
            bg=GUI_DATA.colors.mid_grey_black,
            highlightthickness=0,
        )
        self.button_search = tk.Canvas(
            self,
            width=54,
            height=54,
            bg=GUI_DATA.colors.mid_grey_black,
            highlightthickness=0,
        )
        self.button_settings = tk.Canvas(
            self,
            width=54,
            height=54,
            bg=GUI_DATA.colors.mid_grey_black,
            highlightthickness=0,
        )
        self.button_download = tk.Canvas(
            self,
            width=54,
            height=54,
            bg=GUI_DATA.colors.mid_grey_black,
            highlightthickness=0,
        )
        self.button_language.place(relx=0.2, rely=0.5, anchor="center")
        self.button_search.place(relx=0.4, rely=0.5, anchor="center")
        self.button_settings.place(relx=0.6, rely=0.5, anchor="center")
        self.button_download.place(relx=0.8, rely=0.5, anchor="center")

        self.button_language.bind("<Enter>", self.enter_tab)
        self.button_search.bind("<Enter>", self.enter_tab)
        self.button_settings.bind("<Enter>", self.enter_tab)
        self.button_download.bind("<Enter>", self.enter_tab)

        self.button_language.bind("<Leave>", self.leave_tab)
        self.button_search.bind("<Leave>", self.leave_tab)
        self.button_settings.bind("<Leave>", self.leave_tab)
        self.button_download.bind("<Leave>", self.leave_tab)
        tk_tools.asset_tab(self.button_language, "language", "rest")
        tk_tools.asset_tab(self.button_search, "search", "rest")
        tk_tools.asset_tab(self.button_settings, "settings", "rest")
        tk_tools.asset_tab(self.button_download, "download", "rest")
        tk_tools.set_default_grid_size(self)
        self.active_tab = active_tab
        self.activate_tabs()

    def activate_tabs(self) -> None:
        if self.active_tab == "language":
            self.tabs["language"].place(x=GUI_DATA.pos.content_x, y=GUI_DATA.pos.content_y, anchor="center")
            tk_tools.asset_tab(self.button_language, "language", "press")
            self.parent.title("subsearch - languages")
        elif self.active_tab == "search":
            self.tabs["search"].place(x=GUI_DATA.pos.content_x, y=GUI_DATA.pos.content_y, anchor="center")
            tk_tools.asset_tab(self.button_search, "search", "press")
            self.parent.title("subsearch - search settings")
        elif self.active_tab == "settings":
            self.tabs["settings"].place(x=GUI_DATA.pos.content_x, y=GUI_DATA.pos.content_y, anchor="center")
            tk_tools.asset_tab(self.button_settings, "settings", "press")
            self.parent.title("subsearch - application settings")
        elif self.active_tab == "download":
            self.tabs["download"].place(x=GUI_DATA.pos.content_x, y=GUI_DATA.pos.content_y, anchor="center")
            tk_tools.asset_tab(self.button_download, "download", "press")
            self.parent.title("subsearch - manual download")

    def release_tab(self, event) -> None:
        if event.widget == self.button_language:
            self.active_tab = "language"
        if event.widget == self.button_search:
            self.active_tab = "search"
        if event.widget == self.button_settings:
            self.active_tab = "settings"
        if event.widget == self.button_download:
            self.active_tab = "download"
        self.activate_tabs()
        self.deactivate_tabs()

    def press_tab(self, event) -> None:
        if event.widget == self.button_language:
            self.button_language.bind("<ButtonRelease>", self.release_tab)
            tk_tools.asset_tab(self.button_language, "language", "press", y=20)
        if event.widget == self.button_search:
            self.button_search.bind("<ButtonRelease>", self.release_tab)
            tk_tools.asset_tab(self.button_search, "search", "press", y=20)
        if event.widget == self.button_settings:
            self.button_settings.bind("<ButtonRelease>", self.release_tab)
            tk_tools.asset_tab(self.button_settings, "settings", "press", y=20)
        if event.widget == self.button_download:
            self.button_download.bind("<ButtonRelease>", self.release_tab)
            tk_tools.asset_tab(self.button_download, "download", "press", y=20)

    def deactivate_tabs(self) -> None:
        if self.active_tab != "language":
            self.tabs["language"].place(x=GUI_DATA.pos.content_hidden_x, y=GUI_DATA.pos.content_y, anchor="nw")
            tk_tools.asset_tab(self.button_language, "language", "rest")
        if self.active_tab != "search":
            self.tabs["search"].place(x=GUI_DATA.pos.content_hidden_x, y=GUI_DATA.pos.content_y, anchor="nw")
            tk_tools.asset_tab(self.button_search, "search", "rest")
        if self.active_tab != "settings":
            self.tabs["settings"].place(x=GUI_DATA.pos.content_hidden_x, y=GUI_DATA.pos.content_y, anchor="nw")
            tk_tools.asset_tab(self.button_settings, "settings", "rest")
        if self.active_tab != "download":
            self.tabs["download"].place(x=GUI_DATA.pos.content_hidden_x, y=GUI_DATA.pos.content_y, anchor="nw")
            tk_tools.asset_tab(self.button_download, "download", "rest")

    def enter_tab(self, event) -> None:
        if event.widget == self.button_language:
            self.button_language.bind("<ButtonPress>", self.press_tab)
            tk_tools.asset_tab(self.button_language, "language", "hover", y=25)
        if event.widget == self.button_search:
            self.button_search.bind("<ButtonPress>", self.press_tab)
            tk_tools.asset_tab(self.button_search, "search", "hover", y=25)
        if event.widget == self.button_settings:
            self.button_settings.bind("<ButtonPress>", self.press_tab)
            tk_tools.asset_tab(self.button_settings, "settings", "hover", y=25)
        if event.widget == self.button_download:
            self.button_download.bind("<ButtonPress>", self.press_tab)
            tk_tools.asset_tab(self.button_download, "download", "hover", y=25)

    def leave_tab(self, event) -> None:
        if event.widget == self.button_language:
            self.button_language.unbind("<ButtonPress>")
        if event.widget == self.button_search:
            self.button_search.unbind("<ButtonPress>")
        if event.widget == self.button_settings:
            self.button_settings.unbind("<ButtonPress>")
        if event.widget == self.button_download:
            self.button_download.unbind("<ButtonPress>")
        self.activate_tabs()
        self.deactivate_tabs()


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
    tabs = {
        "language": TabLanguage(root),
        "search": TabSearch(root),
        "settings": TabSettings(root),
        "download": TabDownload(root, formatted_data),
    }
    # edit_tabs(tabs, "language").place(x=32)
    footer = Footer(root, tabs, active_tab.lower())
    footer.place(y=GUI_DATA.size.root_height - 82)
    root.mainloop()


def main():
    if raw_registry.registry_key_exists() is False:
        raw_config.set_default_json()
        raw_registry.add_context_menu()
    root = tk.Tk(className=f"subsearch")
    root.configure(background=GUI_DATA.colors.dark_grey)
    root.iconbitmap(__paths__.icon)
    root.geometry(tk_tools.WindowPosition.set(root))
    root.resizable(False, False)
    return root
