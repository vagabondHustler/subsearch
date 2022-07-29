import tkinter as tk
from tkinter import ttk
import sv_ttk


import os
import sys
import tkinter as tk
from tkinter import ttk

import sv_ttk
from src.gui.root import Tks, main
from src.scraper.subscene_soup import get_download_url
from src.utilities.file_manager import clean_up, download_zip_auto, extract_zips
from src.utilities.local_paths import cwd


# file with subtitles and corresponding dl links
def read_tmp_file(file: str) -> list[str]:
    if os.path.exists(file):
        with open(file, "r") as f:
            return [line.strip() for line in f]


# download said subtitle to the folder with the video file in it


class DownloadList(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        # listbox for the subtitles
        self.extent = 0
        sublist = read_tmp_file("tmp.txt")
        self.sublist_lenght = len(sublist)
        self.hs = ttk.Scrollbar(root, orient="vertical", style="Vertical.TScrollbar")
        sub_listbox = tk.Listbox(
            root,
            bg=Tks.dark_grey,
            fg=Tks.light_grey,
            font=Tks.font8b,
            bd=0,
            border=0,
            borderwidth=0,
            highlightthickness=0,
            yscrollcommand=self.hs.set,
        )
        sub_listbox.place(
            height=Tks.window_height - 60,
            width=Tks.window_width - 20,
            relx=0.5,
            rely=0.525,
            bordermode="inside",
            anchor="center",
        )
        self.count = 0
        self.sub_listbox = sub_listbox
        self.sublist = sublist
        self.fill_listbox()

        # custom scrollbar
        scrollbar_lengt = 50
        self.scrollbar_lengt = scrollbar_lengt
        self.scrollbar_lenght_half = round(scrollbar_lengt / 2)
        style = ttk.Style()
        style.theme_use("sun-valley-dark")
        style.element_options("Vertical.TScrollbar.thumb")
        # configure the style
        style.configure(
            "Vertical.TScrollbar",
            gripcount=0,
            state="disable",
            relief="flat",
            borderwidth=0,
            bd=0,
            arrowsize=24,
        )

        self.hs.place(x=Tks.window_width - 28, y=51, bordermode="inside", height=633)
        self.hs.config(command=self.sub_listbox.yview)
        self.hs.lift()

    def fill_listbox(self):
        dicts_names = {}
        dicts_urls = {}

        # fil list box with all available subtitles that were found and not downloaded
        for x, i in zip(range(0, self.sublist_lenght), self.sublist):
            x = i.split(" ")
            match = f"{x[0]} {x[1]}"
            name = x[2]
            url = x[-1]
            txt = f"{match} {name}"
            self.sub_listbox.insert(tk.END, f"{match} {name}\n")
            self.sub_listbox.bind("<<ListboxSelect>>", self.download_button)
            dicts_names[self.count] = txt
            dicts_urls[self.count] = url
            self.dicts_urls = dicts_urls
            self.dicts_names = dicts_names
            self.count += 1

    def download_button(self, event):
        _i = str(self.sub_listbox.curselection())
        _i = _i.replace("(", "")
        _i = _i.replace(")", "")
        items = _i.replace(",", "")
        _error = False
        for (number, url), (name) in zip(self.dicts_urls.items(), self.dicts_names.values()):
            if number == int(items):
                self.sub_listbox.delete(int(number))
                self.sub_listbox.insert(int(number), f"»»» DOWNLOADING «««")
                self.sub_listbox.itemconfig(int(number), {"fg": Tks.blue})
                try:
                    dl_url = get_download_url(url)
                    _name = name.replace("/", "").replace("\\", "").split(": ")
                    path = f"{cwd()}\\{_name[-1]}.zip"
                    item = path, dl_url, 1, 1
                    download_zip_auto(item)
                    if _error is False:
                        extract_zips(cwd(), ".zip")
                        clean_up(cwd(), ".zip")
                        clean_up(cwd(), ").nfo")
                        self.sub_listbox.delete(int(number))
                        self.sub_listbox.insert(int(number), f"✔ {name}")
                        self.sub_listbox.itemconfig(int(number), {"fg": Tks.green})
                        _error = False
                except OSError:
                    _error = True
                    self.sub_listbox.delete(int(number))
                    self.sub_listbox.insert(int(number), f"⚠⚠⚠ Download failed ⚠⚠⚠")
                    self.sub_listbox.itemconfig(int(number), {"fg": Tks.red})


root = main()
sv_ttk.set_theme("dark")
root.configure(bg="#1c1c1c")
DownloadList(root).pack(anchor="center")
tk.Frame(root, bg=Tks.dark_grey).pack(anchor="center", expand=True)
root.mainloop()


sys.exit()
