import re
import tkinter as tk
from tkinter import ttk

from subsearch.data import GUI_DATA, video_data
from subsearch.data.data_objects import DownloadMetaData, FormattedMetadata
from subsearch.providers import subscene
from subsearch.utils import file_manager, log


class DownloadList(tk.Frame):
    def __init__(self, parent, formatted_data: list[FormattedMetadata]) -> None:
        tk.Frame.__init__(self, parent)
        root_posx, root_posy = parent.winfo_reqwidth(), parent.winfo_reqheight()
        self.configure(bg=GUI_DATA.colors.dark_grey, width=root_posx, height=root_posy - 82)
        # listbox for the subtitles
        if formatted_data is not None:
            formatted_data.sort(key=lambda x: x.pct_result, reverse=True)
        self.formatted_data = formatted_data
        self.subscene_scrape = subscene.SubsceneScraper()
        self.extent = 0
        # self.sublist = read_tmp_file()
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", style="Vertical.TScrollbar")
        self.sub_listbox = tk.Listbox(
            self,
            height=root_posy,
            bg=GUI_DATA.colors.dark_grey,
            fg=GUI_DATA.colors.light_grey,
            font=GUI_DATA.fonts.cas8b,
            bd=0,
            border=0,
            borderwidth=0,
            highlightthickness=0,
            activestyle="none",
            yscrollcommand=self.scrollbar.set,
        )
        hsx, _hsy = self.scrollbar.winfo_reqwidth(), self.scrollbar.winfo_reqheight()
        self.sub_listbox.place(
            height=root_posy - 82,
            width=root_posx - hsx - 20,
            x=18,
            rely=0.5,
            bordermode="inside",
            anchor="w",
        )
        if self.formatted_data is not None:
            self.fill_listbox()
        self.scrollbar.place(x=root_posx - 17, y=0, bordermode="inside", height=root_posy - 82)
        self.scrollbar.config(command=self.sub_listbox.yview)
        self.scrollbar.lift()

    def fill_listbox(self) -> None:
        self._providers = {}
        self._releases = {}
        self._urls = {}
        log.output("")
        log.output_header("Processing files with GUI")
        # fil list box with all available subtitles that were found and not downloaded
        for enu, data in enumerate(self.formatted_data):
            self.sub_listbox.insert(tk.END, f"{data.formatted_release}\n")
            self.sub_listbox.bind("<ButtonPress-1>", self.mouse_b1_press)
            self._providers[enu] = data.provider
            self._releases[enu] = data.release
            self._urls[enu] = data.url

    def mouse_b1_press(self, event) -> None:
        self.sub_listbox.bind("<<ListboxSelect>>", self.download_button)

    def mouse_b1_release(self, event) -> None:
        self.sub_listbox.bind("<ButtonPress-1>", self.mouse_b1_press)

    def download_button(self, event) -> None:
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
            self.sub_listbox.itemconfig(int(enum), {"fg": GUI_DATA.colors.blue})
            if _provider == "subscene":
                download_url = self.subscene_scrape.get_download_url(_url)
            else:
                download_url = _url
            path = f"{video_data.tmp_directory}\\__{_provider}__{item_num}.zip"
            enum = DownloadMetaData(
                provider=f"Downloading from {_provider}",
                name=_release,
                file_path=path,
                url=download_url,
                idx_num=1,
                idx_lenght=1,
            )  # type: ignore
            file_manager.download_subtitle(enum)  # type: ignore
            file_manager.extract_files(video_data.tmp_directory, video_data.subs_directory, ".zip")
            file_manager.clean_up_files(video_data.tmp_directory, "zip")
            break
        self.sub_listbox.delete(int(item_num))
        self.sub_listbox.insert(int(item_num), f"✔ {_release}")
        self.sub_listbox.itemconfig(int(item_num), {"fg": GUI_DATA.colors.green})
