import tkinter as tk

from subsearch.gui import (
    base_root,
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
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TKCOLOR.mid_grey_black, width=TKWINDOW.width - 4, height=80)
        
        self.language_grey_path = tk_tools.get_button_path("language_grey.png")
        self.search_grey_path = tk_tools.get_button_path("search_grey.png")
        self.settings_grey_path = tk_tools.get_button_path("settings_grey.png")

        self.language_silver_path = tk_tools.get_button_path("language_silver.png")
        self.search_silver_path = tk_tools.get_button_path("search_silver.png")
        self.settings_silver_path = tk_tools.get_button_path("settings_silver.png")

        self.language_white_path = tk_tools.get_button_path("language_white.png")
        self.search_white_path = tk_tools.get_button_path("search_white.png")
        self.settings_white_path = tk_tools.get_button_path("settings_white.png")
        
        self.language_grey_png = tk.PhotoImage(file=self.language_grey_path)
        self.search_grey_png = tk.PhotoImage(file=self.search_grey_path)
        self.settings_grey_png = tk.PhotoImage(file=self.settings_grey_path)
        
        self.language_silver_png = tk.PhotoImage(file=self.language_silver_path)
        self.search_silver_png = tk.PhotoImage(file=self.search_silver_path)
        self.settings_silver_png = tk.PhotoImage(file=self.settings_silver_path)
        
        self.language_white_png = tk.PhotoImage(file=self.language_white_path)
        self.search_white_png = tk.PhotoImage(file=self.search_white_path)
        self.settings_white_png = tk.PhotoImage(file=self.settings_white_path)
        
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
        self.language.place(relx=0.2, rely=0.5, anchor="center")
        self.search.place(relx=0.5, rely=0.5, anchor="center")
        self.settings.place(relx=0.8, rely=0.5, anchor="center")

        self.language.bind("<Enter>", self.enter_tab)
        self.search.bind("<Enter>", self.enter_tab)
        self.settings.bind("<Enter>", self.enter_tab)
        
        self.language.bind("<Leave>", self.leave_tab)
        self.search.bind("<Leave>", self.leave_tab)
        self.settings.bind("<Leave>", self.leave_tab)
        
        self.update_img(self.language, self.language_grey_png)
        self.update_img(self.search, self.search_grey_png)
        self.update_img(self.settings, self.settings_grey_png)

        self.active_window = "language"
        _tab_language.place(relx=0.5, rely=0.5, anchor="center")
        self.update_img(self.language, self.language_white_png)
        tk_tools.set_default_grid_size(self)

    def release_tab(self, event):
        if event.widget == self.language:
            self.active_window = "language"
            _tab_language.place(relx=0.5, rely=0.5, anchor="center")
            self.update_img(self.language, self.language_white_png)
        if event.widget == self.search:
            self.active_window = "search"
            _tab_search.place(relx=0.5, rely=0.5, anchor="center")
            self.update_img(self.search, self.search_white_png)
        if event.widget == self.settings:
            self.active_window = "settings"
            _subsearch_tab.place(relx=0.5, rely=0.5, anchor="center")
            self.update_img(self.settings, self.settings_white_png)
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

    def deactivate_tabs(self):
        if self.active_window != "language":
            _tab_language.place(relx=1, rely=0.5, anchor="nw")
            self.update_img(self.language, self.language_grey_png)

        if self.active_window != "search":
            _tab_search.place(relx=1, rely=0.5, anchor="nw")
            self.update_img(self.search, self.search_grey_png)

        if self.active_window != "settings":
            _subsearch_tab.place(relx=1, rely=0.5, anchor="nw")
            self.update_img(self.settings, self.settings_grey_png)

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

    def leave_tab(self, event):
        if event.widget == self.language:
            self.language.unbind("<ButtonPress>")
        if event.widget == self.search:
            self.search.unbind("<ButtonPress>")
        if event.widget == self.settings:
            self.settings.unbind("<ButtonPress>")
        self.deactivate_tabs()

    def update_img(self, canvas, img, x=27, y=27):
        canvas.delete("all")
        canvas.create_image(x, y, image=img)
        canvas.photoimage = img


class TabLanguageSettings(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TKCOLOR.dark_grey)
        tab_language.SelectLanguage(self).pack(anchor="center")


class TabSearchSettings(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TKCOLOR.dark_grey)
        tab_search.Providers(self).pack(anchor="center")
        tab_search.HearingImparedSubs(self).pack(anchor="center")
        tab_search.SearchThreshold(self).pack(anchor="center")


class TabSubsearchSettings(tk.Frame):
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


def show_widget():
    global _tab_language, _tab_search, _subsearch_tab

    root = base_root.main()
    content = tk.Frame(root, bg=TKCOLOR.dark_grey, width=TKWINDOW.width - 4, height=TKWINDOW.height - 120)
    content.place(x=2, y=40)
    _tab_language = TabLanguageSettings(content)
    _tab_search = TabSearchSettings(content)
    _subsearch_tab = TabSubsearchSettings(content)
    footer = Footer(root)
    footer.place(x=2, y=TKWINDOW.height - 82)

    root.mainloop()
