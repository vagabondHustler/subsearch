import tkinter as tk

import sv_ttk

from subsearch.gui import (
    base_root,
    tab_download,
    tab_language,
    tab_search,
    tab_subsearch,
    tk_data,
    tk_tools,
)
from subsearch.utils import current_user

TKWINDOW = tk_data.Window()
TKCOLOR = tk_data.Color()
TKFONT = tk_data.Font()


class Footer(tk.Frame):
    def __init__(self, parent, active_tab: str, language_tab, search_tab, settings_tab, download_tab):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TKCOLOR.mid_grey_black, width=TKWINDOW.width - 4, height=80)
        self.language_tab = language_tab
        self.search_tab = search_tab
        self.settings_tab = settings_tab
        self.download_tab = download_tab

        self.language_grey_path = tk_tools.get_tabs_png("language_grey.png")
        self.search_grey_path = tk_tools.get_tabs_png("search_grey.png")
        self.settings_grey_path = tk_tools.get_tabs_png("settings_grey.png")
        self.download_grey_path = tk_tools.get_tabs_png("download_grey.png")

        self.language_silver_path = tk_tools.get_tabs_png("language_silver.png")
        self.search_silver_path = tk_tools.get_tabs_png("search_silver.png")
        self.settings_silver_path = tk_tools.get_tabs_png("settings_silver.png")
        self.download_silver_path = tk_tools.get_tabs_png("download_silver.png")

        self.language_white_path = tk_tools.get_tabs_png("language_white.png")
        self.search_white_path = tk_tools.get_tabs_png("search_white.png")
        self.settings_white_path = tk_tools.get_tabs_png("settings_white.png")
        self.download_white_path = tk_tools.get_tabs_png("download_white.png")

        self.language_grey_png = tk.PhotoImage(file=self.language_grey_path)
        self.search_grey_png = tk.PhotoImage(file=self.search_grey_path)
        self.settings_grey_png = tk.PhotoImage(file=self.settings_grey_path)
        self.download_grey_png = tk.PhotoImage(file=self.download_grey_path)

        self.language_silver_png = tk.PhotoImage(file=self.language_silver_path)
        self.search_silver_png = tk.PhotoImage(file=self.search_silver_path)
        self.settings_silver_png = tk.PhotoImage(file=self.settings_silver_path)
        self.download_silver_png = tk.PhotoImage(file=self.download_silver_path)

        self.language_white_png = tk.PhotoImage(file=self.language_white_path)
        self.search_white_png = tk.PhotoImage(file=self.search_white_path)
        self.settings_white_png = tk.PhotoImage(file=self.settings_white_path)
        self.download_white_png = tk.PhotoImage(file=self.download_white_path)

        self.language = tk.Canvas(
            self,
            width=54,
            height=54,
            bg=TKCOLOR.mid_grey_black,
            highlightthickness=0,
        )
        self.search = tk.Canvas(
            self,
            width=54,
            height=54,
            bg=TKCOLOR.mid_grey_black,
            highlightthickness=0,
        )
        self.settings = tk.Canvas(
            self,
            width=54,
            height=54,
            bg=TKCOLOR.mid_grey_black,
            highlightthickness=0,
        )
        self.download = tk.Canvas(
            self,
            width=54,
            height=54,
            bg=TKCOLOR.mid_grey_black,
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

        self.update_img(self.language, self.language_grey_png)
        self.update_img(self.search, self.search_grey_png)
        self.update_img(self.settings, self.settings_grey_png)
        self.update_img(self.download, self.download_grey_png)
        tk_tools.set_default_grid_size(self)
        self.active_tab = active_tab
        self.activate_tabs()

    def activate_tabs(self):
        if self.active_tab == "language":
            self.language_tab.place(relx=0.5, rely=0.5, anchor="center")
            self.update_img(self.language, self.language_white_png)
        elif self.active_tab == "search":
            self.search_tab.place(relx=0.5, rely=0.5, anchor="center")
            self.update_img(self.search, self.search_white_png)
        elif self.active_tab == "settings":
            self.settings_tab.place(relx=0.5, rely=0.5, anchor="center")
            self.update_img(self.settings, self.settings_white_png)
        elif self.active_tab == "download":
            self.download_tab.place(relx=0.5, rely=0.5, anchor="center")
            self.update_img(self.download, self.download_white_png)

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
            self.update_img(self.language, self.language_white_png, y=20)
        if event.widget == self.search:
            self.search.bind("<ButtonRelease>", self.release_tab)
            self.update_img(self.search, self.search_white_png, y=20)
        if event.widget == self.settings:
            self.settings.bind("<ButtonRelease>", self.release_tab)
            self.update_img(self.settings, self.settings_white_png, y=20)
        if event.widget == self.download:
            self.download.bind("<ButtonRelease>", self.release_tab)
            self.update_img(self.download, self.download_white_png, y=20)

    def deactivate_tabs(self):
        if self.active_tab != "language":
            self.language_tab.place(relx=1, rely=0.5, anchor="nw")
            self.update_img(self.language, self.language_grey_png)
        if self.active_tab != "search":
            self.search_tab.place(relx=1, rely=0.5, anchor="nw")
            self.update_img(self.search, self.search_grey_png)
        if self.active_tab != "settings":
            self.settings_tab.place(relx=1, rely=0.5, anchor="nw")
            self.update_img(self.settings, self.settings_grey_png)
        if self.active_tab != "download":
            self.download_tab.place(relx=1, rely=0.5, anchor="nw")
            self.update_img(self.download, self.download_grey_png)

    def enter_tab(self, event):
        if event.widget == self.language:
            self.language.bind("<ButtonPress>", self.press_tab)
            self.update_img(self.language, self.language_silver_png, y=25)
        if event.widget == self.search:
            self.search.bind("<ButtonPress>", self.press_tab)
            self.update_img(self.search, self.search_silver_png, y=25)
        if event.widget == self.settings:
            self.settings.bind("<ButtonPress>", self.press_tab)
            self.update_img(self.settings, self.settings_silver_png, y=25)
        if event.widget == self.download:
            self.download.bind("<ButtonPress>", self.press_tab)
            self.update_img(self.download, self.download_silver_png, y=25)

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

    def update_img(self, canvas, img, x=27, y=27):
        canvas.delete("all")
        canvas.create_image(x, y, image=img)
        canvas.photoimage = img


class TabLanguage(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TKCOLOR.dark_grey)
        tab_language.SelectLanguage(self).pack(anchor="center")


class TabSearch(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TKCOLOR.dark_grey)
        tab_search.Providers(self).pack(anchor="center")
        tab_search.HearingImpairedSubs(self).pack(anchor="center")
        tab_search.SearchThreshold(self).pack(anchor="center")


class TabSettings(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TKCOLOR.dark_grey)
        tab_subsearch.FileExtensions(self).pack(anchor="center")
        tk.Frame(self, height=80, bg=TKCOLOR.dark_grey).pack(anchor="center", expand=True)
        tab_subsearch.ShowContextMenu(self).pack(anchor="center")
        tab_subsearch.ShowContextMenuIcon(self).pack(anchor="center")
        tab_subsearch.ShowDownloadWindow(self).pack(anchor="center")
        if current_user.check_is_exe() is False:
            tab_subsearch.ShowTerminalOnSearch(self).pack(anchor="center")
        tk.Frame(self, height=20, bg=TKCOLOR.dark_grey).pack(anchor="center", expand=True)
        tab_subsearch.CheckForUpdates(self).pack(anchor="center")


class TabDownload(tk.Frame):
    def __init__(self, parent, con_x, con_y):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TKCOLOR.dark_grey)
        sv_ttk.set_theme("dark")
        tab_download.DownloadList(self, con_x, con_y).pack(anchor="center")


def open_tab(active_tab: str):
    root = base_root.main()
    content = tk.Frame(root, bg=TKCOLOR.dark_grey, width=TKWINDOW.width - 4, height=TKWINDOW.height - 118)
    content.place(x=2, y=37)
    conx, cony = content.winfo_reqwidth(), content.winfo_reqheight()
    footer = Footer(
        root,
        active_tab.lower(),
        TabLanguage(content),
        TabSearch(content),
        TabSettings(content),
        TabDownload(content, conx, cony),
    )
    footer.place(x=2, y=TKWINDOW.height - 82)

    root.mainloop()
