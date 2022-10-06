import re
import tkinter as tk
from tkinter import ttk

from subsearch.data import __video__
from subsearch.data.data_fields import DownloadData, FormattedData, TkColor, TkFont
from subsearch.providers import subscene
from subsearch.utils import file_manager, log


# download said subtitle to the folder with the video file in it
class DownloadList(tk.Frame):
    def __init__(self, parent, con_x, con_y, formatted_data: list[FormattedData]):
        tk.Frame.__init__(self, parent)
        self.configure(bg=TkColor().dark_grey, width=con_x, height=con_y)
        # listbox for the subtitles
        if formatted_data is not None:
            formatted_data.sort(key=lambda x: x.pct_result, reverse=True)
        self.formatted_data = formatted_data
        self.subscene_scrape = subscene.SubsceneScrape()
        self.extent = 0
        # self.sublist = read_tmp_file()
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", style="Vertical.TScrollbar")
        self.sub_listbox = tk.Listbox(
            self,
            height=con_y,
            bg=TkColor().dark_grey,
            fg=TkColor().light_grey,
            font=TkFont().cas8b,
            bd=0,
            border=0,
            borderwidth=0,
            highlightthickness=0,
            activestyle="none",
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
        if self.formatted_data is not None:
            self.fill_listbox()
        self.scrollbar.place(x=con_x - 17, y=0, bordermode="inside", height=con_y)
        self.scrollbar.config(command=self.sub_listbox.yview)
        self.scrollbar.lift()

    def fill_listbox(self):
        self._providers = {}
        self._releases = {}
        self._urls = {}
        log.output("")
        log.output_header("[Processing files with GUI]")
        # fil list box with all available subtitles that were found and not downloaded
        for enu, data in enumerate(self.formatted_data):
            self.sub_listbox.insert(tk.END, f"{data.formatted_release}\n")
            self.sub_listbox.bind("<ButtonPress-1>", self.mouse_b1_press)
            self._providers[enu] = data.provider
            self._releases[enu] = data.release
            self._urls[enu] = data.url

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
        for enum, _provider, _release, _url in zip(
            self._providers.keys(), self._providers.values(), self._releases.values(), self._urls.values()
        ):
            if enum != int(item_num):
                continue
            self.sub_listbox.itemconfig(int(enum), {"fg": TkColor().blue})
            if _provider == "subscene":
                download_url = self.subscene_scrape.get_download_url(_url)
            else:
                download_url = _url
            path = f"{__video__.tmp_directory}\\__{_provider}__{item_num}.zip"
            enum = DownloadData(
                provider=f"Downloading from {_provider}",
                name=_release,
                file_path=path,
                url=download_url,
                idx_num=1,
                idx_lenght=1,
            )
            file_manager.download_subtitle(enum)
            file_manager.extract_files(__video__.tmp_directory, __video__.subs_directory, ".zip")
            file_manager.clean_up_files(__video__.tmp_directory, "zip")
            break
        self.sub_listbox.delete(int(item_num))
        self.sub_listbox.insert(int(item_num), f"✔ {_release}")
        self.sub_listbox.itemconfig(int(item_num), {"fg": TkColor().green})
