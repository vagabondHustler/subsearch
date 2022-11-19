import tkinter as tk

from subsearch import gui
from subsearch.data.data_fields import FormattedData, TkColor, TkWindowSize
from subsearch.gui import (
    base_root,
    tab_download,
    tab_language,
    tab_search,
    tab_subsearch,
    tk_tools,
)
from subsearch.utils import current_user


class Footer(tk.Frame):
    def __init__(self, parent, active_tab: str, language_tab, search_tab, settings_tab, download_tab):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TkColor().mid_grey_black, width=TkWindowSize().width - 4, height=80)
        self.language_tab = language_tab
        self.search_tab = search_tab
        self.settings_tab = settings_tab
        self.download_tab = download_tab
        self.language = tk.Canvas(
            self,
            width=54,
            height=54,
            bg=TkColor().mid_grey_black,
            highlightthickness=0,
        )
        self.search = tk.Canvas(
            self,
            width=54,
            height=54,
            bg=TkColor().mid_grey_black,
            highlightthickness=0,
        )
        self.settings = tk.Canvas(
            self,
            width=54,
            height=54,
            bg=TkColor().mid_grey_black,
            highlightthickness=0,
        )
        self.download = tk.Canvas(
            self,
            width=54,
            height=54,
            bg=TkColor().mid_grey_black,
            highlightthickness=0,
        )
        self.language.place(relx=0.2, rely=0.5, anchor="center")
        self.search.place(relx=0.4, rely=0.5, anchor="center")
        self.settings.place(relx=0.6, rely=0.5, anchor="center")
        self.download.place(relx=0.8, rely=0.5, anchor="center")

        self.language.bind("<Enter>", self.enter_tab)
        self.search.bind("<Enter>", self.enter_tab)
        self.settings.bind("<Enter>", self.enter_tab)
        self.download.bind("<Enter>", self.enter_tab)

        self.language.bind("<Leave>", self.leave_tab)
        self.search.bind("<Leave>", self.leave_tab)
        self.settings.bind("<Leave>", self.leave_tab)
        self.download.bind("<Leave>", self.leave_tab)
        tk_tools.asset_tab(self.language, "language", "rest")
        tk_tools.asset_tab(self.search, "search", "rest")
        tk_tools.asset_tab(self.settings, "settings", "rest")
        tk_tools.asset_tab(self.download, "download", "rest")
        tk_tools.set_default_grid_size(self)
        self.active_tab = active_tab
        self.activate_tabs()

    def activate_tabs(self):
        if self.active_tab == "language":
            self.language_tab.place(relx=0.5, rely=0.5, anchor="center")
            tk_tools.asset_tab(self.language, "language", "press")
        elif self.active_tab == "search":
            self.search_tab.place(relx=0.5, rely=0.5, anchor="center")
            tk_tools.asset_tab(self.search, "search", "press")
        elif self.active_tab == "settings":
            self.settings_tab.place(relx=0.5, rely=0.5, anchor="center")
            tk_tools.asset_tab(self.settings, "settings", "press")
        elif self.active_tab == "download":
            self.download_tab.place(relx=0.5, rely=0.5, anchor="center")
            tk_tools.asset_tab(self.download, "download", "press")

    def release_tab(self, event):
        if event.widget == self.language:
            self.active_tab = "language"
        if event.widget == self.search:
            self.active_tab = "search"
        if event.widget == self.settings:
            self.active_tab = "settings"
        if event.widget == self.download:
            self.active_tab = "download"
        self.activate_tabs()
        self.deactivate_tabs()

    def press_tab(self, event):
        if event.widget == self.language:
            self.language.bind("<ButtonRelease>", self.release_tab)
            tk_tools.asset_tab(self.language, "language", "press", y=20)
        if event.widget == self.search:
            self.search.bind("<ButtonRelease>", self.release_tab)
            tk_tools.asset_tab(self.search, "search", "press", y=20)
        if event.widget == self.settings:
            self.settings.bind("<ButtonRelease>", self.release_tab)
            tk_tools.asset_tab(self.settings, "settings", "press", y=20)
        if event.widget == self.download:
            self.download.bind("<ButtonRelease>", self.release_tab)
            tk_tools.asset_tab(self.download, "download", "press", y=20)

    def deactivate_tabs(self):
        if self.active_tab != "language":
            self.language_tab.place(relx=1, rely=0.5, anchor="nw")
            tk_tools.asset_tab(self.language, "language", "rest")
        if self.active_tab != "search":
            self.search_tab.place(relx=1, rely=0.5, anchor="nw")
            tk_tools.asset_tab(self.search, "search", "rest")
        if self.active_tab != "settings":
            self.settings_tab.place(relx=1, rely=0.5, anchor="nw")
            tk_tools.asset_tab(self.settings, "settings", "rest")
        if self.active_tab != "download":
            self.download_tab.place(relx=1, rely=0.5, anchor="nw")
            tk_tools.asset_tab(self.download, "download", "rest")

    def enter_tab(self, event):
        if event.widget == self.language:
            self.language.bind("<ButtonPress>", self.press_tab)
            tk_tools.asset_tab(self.language, "language", "hover", y=25)
        if event.widget == self.search:
            self.search.bind("<ButtonPress>", self.press_tab)
            tk_tools.asset_tab(self.search, "search", "hover", y=25)
        if event.widget == self.settings:
            self.settings.bind("<ButtonPress>", self.press_tab)
            tk_tools.asset_tab(self.settings, "settings", "hover", y=25)
        if event.widget == self.download:
            self.download.bind("<ButtonPress>", self.press_tab)
            tk_tools.asset_tab(self.download, "download", "hover", y=25)

    def leave_tab(self, event):
        if event.widget == self.language:
            self.language.unbind("<ButtonPress>")
        if event.widget == self.search:
            self.search.unbind("<ButtonPress>")
        if event.widget == self.settings:
            self.settings.unbind("<ButtonPress>")
        if event.widget == self.download:
            self.download.unbind("<ButtonPress>")
        self.activate_tabs()
        self.deactivate_tabs()


class TabLanguage(tk.Frame):
    def __init__(self, parent, content_posx, content_posy):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TkColor().dark_grey)
        tab_language.SelectLanguage(self).pack(anchor="center", expand=True)


class TabSearch(tk.Frame):
    def __init__(self, parent, content_posx, content_posy):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TkColor().dark_grey)
        tab_search.Providers(self).pack(anchor="center")
        tk.Frame(self, height=80, bg=TkColor().dark_grey).pack(anchor="center", expand=True)
        tab_search.SubtitleType(self).pack(anchor="center")
        tab_search.SearchThreshold(self).pack(anchor="center")
        tab_search.RenameBestMatch(self).pack(anchor="center")


class TabSettings(tk.Frame):
    def __init__(self, parent, content_posx, content_posy):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TkColor().dark_grey)
        tab_subsearch.FileExtensions(self).pack(anchor="center")
        tk.Frame(self, height=80, bg=TkColor().dark_grey).pack(anchor="center", expand=True)
        tab_subsearch.ShowContextMenu(self).pack(anchor="center")
        tab_subsearch.ShowContextMenuIcon(self).pack(anchor="center")
        tab_subsearch.ShowDownloadWindow(self).pack(anchor="center")
        tab_subsearch.LogToFile(self).pack(anchor="center")
        if current_user.running_from_exe() is False:
            tab_subsearch.ShowTerminalOnSearch(self).pack(anchor="center")
        tk.Frame(self, height=20, bg=TkColor().dark_grey).pack(anchor="center", expand=True)
        tab_subsearch.CheckForUpdates(self).pack(anchor="center")


class TabDownload(tk.Frame):
    def __init__(self, parent, content_posx, content_posy, formatted_data: list[FormattedData]):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TkColor().dark_grey)
        tab_download.DownloadList(self, content_posx, content_posy, formatted_data).pack(anchor="center")


def open_tab(active_tab: str, **kwargs):
    try:
        formatted_data: list[FormattedData] = kwargs["formatted_data"]
    except KeyError:
        formatted_data = None
    root = base_root.main()
    gui.set_theme("dark")
    content = tk.Frame(root, bg=TkColor().dark_grey, width=TkWindowSize().width - 4, height=TkWindowSize().height - 118)
    content.place(x=2, y=37)
    content_posx, content_posy = content.winfo_reqwidth(), content.winfo_reqheight()

    footer = Footer(
        root,
        active_tab.lower(),
        TabLanguage(content, content_posx, content_posy),
        TabSearch(content, content_posx, content_posy),
        TabSettings(content, content_posx, content_posy),
        TabDownload(content, content_posx, content_posy, formatted_data),
    )
    footer.place(x=2, y=TkWindowSize().height - 82)
    root.mainloop()
