import os
import re
import tkinter as tk
from tkinter import ttk

from subsearch.data import __video__
from subsearch.gui import tk_data
from subsearch.providers import subscene
from subsearch.providers.generic import DownloadData
from subsearch.utils import file_manager, log

TKWINDOW = tk_data.Window()
TKCOLOR = tk_data.Color()
TKFONT = tk_data.Font()
# file with subtitles and corresponding dl links
def read_tmp_file():
    if __video__.tmp_directory == None:
        return None

    file = os.path.join(__video__.tmp_directory, "download_data.tmp")
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
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", style="Vertical.TScrollbar")
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
            yscrollcommand=self.scrollbar.set,
        )
        hsx, hsy = self.scrollbar.winfo_reqwidth(), self.scrollbar.winfo_reqheight()
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
        self.scrollbar.place(x=con_x - 17, y=0, bordermode="inside", height=con_y)
        self.scrollbar.config(command=self.sub_listbox.yview)
        self.scrollbar.lift()

    def fill_listbox(self):
        dicts_names = {}
        dicts_urls = {}
        log.output("\n[Proccessing downloads]")
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
        selection = str(self.sub_listbox.curselection())
        item_num = re.findall("(\d+)", selection)[0]
        self.sub_listbox.delete(int(item_num))
        self.sub_listbox.insert(int(item_num), f"» DOWNLOADING «")
        for (number, _url), (_name) in zip(self.dicts_urls.items(), self.dicts_names.values()):
            if number != int(item_num):
                continue
            self.sub_listbox.itemconfig(int(number), {"fg": TKCOLOR.blue})
            dl_url = self.subscene_scrape.download_url(_url)
            _name = "".join(re.findall("[^\/\\\:\?\<\>\|\*]*", _name))
            path = f"{__video__.tmp_directory}\\__subsearch__{item_num}.zip"
            item = DownloadData(name=_name, file_path=path, url=dl_url, idx_num=1, idx_lenght=1)
            file_manager.download_subtitle(item)
            file_manager.extract_files(__video__.tmp_directory, __video__.subs_directory, ".zip")
            break
        self.sub_listbox.delete(int(item_num))
        self.sub_listbox.insert(int(item_num), f"✔ {_name}")
        self.sub_listbox.itemconfig(int(item_num), {"fg": TKCOLOR.green})
