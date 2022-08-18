import os
import tkinter as tk
from tkinter import ttk

import sv_ttk

from subsearch.data import __video_directory__
from subsearch.gui import tkdata, widget_root
from subsearch.scraper import subscene_soup
from subsearch.utils import file_manager

TKWINDOW = tkdata.Window()
TKCOLOR = tkdata.Color()
TKFONT = tkdata.Font()
# file with subtitles and corresponding dl links
def read_tmp_file():
    file = os.path.join(__video_directory__, "__subsearch__dl_data.tmp")
    with open(file, "r") as f:
        return [line.strip() for line in f]


# download said subtitle to the folder with the video file in it
class DownloadList(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        # listbox for the subtitles
        self.extent = 0
        self.sublist = read_tmp_file()
        self.hs = ttk.Scrollbar(root, orient="vertical", style="Vertical.TScrollbar")
        sub_listbox = tk.Listbox(
            root,
            bg=TKCOLOR.dark_grey,
            fg=TKCOLOR.light_grey,
            font=TKFONT.cas8b,
            bd=0,
            border=0,
            borderwidth=0,
            highlightthickness=0,
            yscrollcommand=self.hs.set,
        )
        sub_listbox.place(
            height=TKWINDOW.height - 60,
            width=TKWINDOW.width - 20,
            relx=0.5,
            rely=0.525,
            bordermode="inside",
            anchor="center",
        )
        self.sub_listbox = sub_listbox
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

        self.hs.place(x=TKWINDOW.width - 28, y=51, bordermode="inside", height=633)
        self.hs.config(command=self.sub_listbox.yview)
        self.hs.lift()

    def fill_listbox(self):
        dicts_names = {}
        dicts_urls = {}
        # fil list box with all available subtitles that were found and not downloaded
        for enu, item in enumerate(self.sublist):
            x = item.split(" ")
            match = f"{x[0]} {x[1]}"
            name = x[2]
            url = x[-1]
            txt = f"{match} {name}"
            self.sub_listbox.insert(tk.END, f"{match} {name}\n")
            self.sub_listbox.bind("<ButtonPress-1>", self.mouse_b1_press)
            dicts_names[enu] = txt
            dicts_urls[enu] = url
            self.dicts_urls = dicts_urls
            self.dicts_names = dicts_names

    def mouse_b1_press(self, event):
        self.sub_listbox.bind("<<ListboxSelect>>", self.download_button)

    def mouse_b1_release(self, event):
        self.sub_listbox.bind("<ButtonPress-1>", self.mouse_b1_press)

    def download_button(self, event):
        self.sub_listbox.unbind("<<ListboxSelect>>")
        self.sub_listbox.bind("<ButtonRelease-1>", self.mouse_b1_release)
        _i = str(self.sub_listbox.curselection())
        _i = _i.replace("(", "")
        _i = _i.replace(")", "")
        items = _i.replace(",", "")
        _error = False
        for (number, url), (name) in zip(self.dicts_urls.items(), self.dicts_names.values()):
            if number == int(items):
                self.sub_listbox.delete(int(number))
                self.sub_listbox.insert(int(number), f"»»» DOWNLOADING «««")
                self.sub_listbox.itemconfig(int(number), {"fg": TKCOLOR.blue})
                try:
                    dl_url = subscene_soup.get_download_url(url)
                    _name = name.replace("/", "").replace("\\", "").split(": ")
                    path = f"{__video_directory__}\\__subsearch__{_name[-1]}.zip"
                    item = path, dl_url, 1, 1
                    file_manager.download_zip(item)
                    if _error is False:
                        file_manager.extract_zips(__video_directory__, ".zip")
                        file_manager.clean_up(__video_directory__, ".zip")
                        file_manager.clean_up(__video_directory__, ").nfo")
                        self.sub_listbox.delete(int(number))
                        self.sub_listbox.insert(int(number), f"✔ {name}")
                        self.sub_listbox.itemconfig(int(number), {"fg": TKCOLOR.green})
                        _error = False
                except OSError:
                    _error = True
                    self.sub_listbox.delete(int(number))
                    self.sub_listbox.insert(int(number), f"⚠⚠⚠ Download failed ⚠⚠⚠")
                    self.sub_listbox.itemconfig(int(number), {"fg": TKCOLOR.red})


def show_widget():
    global root
    root = widget_root.main()
    sv_ttk.set_theme("dark")
    DownloadList(root).pack(anchor="center")
    tk.Frame(root, bg=TKCOLOR.dark_grey).pack(anchor="center", expand=True)
    root.mainloop()
