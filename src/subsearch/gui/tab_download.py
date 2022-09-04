import os
import tkinter as tk
from tkinter import ttk

from subsearch.data import __video__
from subsearch.gui import tk_data
from subsearch.providers import subscene
from subsearch.providers.generic import DownloadData
from subsearch.utils import file_manager

TKWINDOW = tk_data.Window()
TKCOLOR = tk_data.Color()
TKFONT = tk_data.Font()
# file with subtitles and corresponding dl links
def read_tmp_file():
    if __video__.directory == None:
        return None

    file = os.path.join(__video__.directory, "__subsearch__dl_data.tmp")
    with open(file, "r") as f:
        return [line.strip() for line in f]


# download said subtitle to the folder with the video file in it
class DownloadList(tk.Frame):
    def __init__(self, parent, con_x, con_y):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TKCOLOR.dark_grey, width=con_x, height=con_y)
        # listbox for the subtitles
        self.subscene_scrape = subscene.SubsceneScrape()
        self.extent = 0
        self.sublist = read_tmp_file()
        self.hs = ttk.Scrollbar(self, orient="vertical", style="Vertical.TScrollbar")
        self.sub_listbox = tk.Listbox(
            self,
            height=con_y,
            bg=TKCOLOR.dark_grey,
            fg=TKCOLOR.light_grey,
            font=TKFONT.cas8b,
            bd=0,
            border=0,
            borderwidth=0,
            highlightthickness=0,
            activestyle=None,
            yscrollcommand=self.hs.set,
        )
        hsx, hsy = self.hs.winfo_reqwidth(), self.hs.winfo_reqheight()
        self.sub_listbox.place(
            height=con_y - 36,
            width=con_x - hsx - 20,
            x=18,
            rely=0.5,
            bordermode="inside",
            anchor="w",
        )
        if self.sublist is not None:
            self.fill_listbox()
        # custom scrollbar
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

        self.hs.place(x=con_x - 17, y=0, bordermode="inside", height=con_y)
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
        for (number, _url), (_name) in zip(self.dicts_urls.items(), self.dicts_names.values()):
            if number == int(items):
                self.sub_listbox.delete(int(number))
                self.sub_listbox.insert(int(number), f"»»» DOWNLOADING «««")
                self.sub_listbox.itemconfig(int(number), {"fg": TKCOLOR.blue})
                try:
                    dl_url = self.subscene_scrape.download_url(_url)
                    _name = _name.replace("/", "").replace("\\", "").split(": ")
                    path = f"{__video__.directory}\\__subsearch__{_name[-1]}.zip"
                    item = DownloadData(name=_name, file_path=path, url=dl_url, idx_num=1, idx_lenght=1)
                    file_manager.download_subtitle(item)
                    if _error is False:
                        file_manager.extract_files(__video__.directory, ".zip")
                        file_manager.clean_up(__video__.directory, ".zip")
                        file_manager.clean_up(__video__.directory, ").nfo")
                        self.sub_listbox.delete(int(number))
                        self.sub_listbox.insert(int(number), f"✔ {_name[0]} {_name[1]}")
                        self.sub_listbox.itemconfig(int(number), {"fg": TKCOLOR.green})
                        _error = False
                except OSError:
                    _error = True
                    self.sub_listbox.delete(int(number))
                    self.sub_listbox.insert(int(number), f"⚠⚠⚠ Download failed ⚠⚠⚠")
                    self.sub_listbox.itemconfig(int(number), {"fg": TKCOLOR.red})
