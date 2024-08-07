import tkinter as tk
from tkinter import ttk

from subsearch.globals import log
from subsearch.globals.constants import FILE_PATHS, VIDEO_FILE
from subsearch.globals.dataclasses import Subtitle
from subsearch.gui import common_utils
from subsearch.gui.resources import config as cfg
from subsearch.providers import subsource
from subsearch.utils import io_file_system, io_toml, string_parser


class DownloadManager(ttk.LabelFrame):
    downloaded_subtitle: list[Subtitle] = []

    def __init__(self, parent, **kwargs) -> None:
        ttk.Labelframe.__init__(self, parent)
        self.configure(text="Available subtitles", padding=10)
        subtitles: list[Subtitle] = kwargs.get("subtitles", [])
        if subtitles:
            subtitles.sort(key=lambda x: x.precentage_result, reverse=True)
        frame_left = tk.Frame(self)
        frame_sep = tk.Frame(self, width=5)
        frame_right = tk.Frame(self)
        frame_left.pack(side=tk.LEFT, expand=True, fill="both")
        frame_sep.pack(side=tk.LEFT, fill="y")
        frame_right.pack(side=tk.LEFT, fill="y")
        self.failed_subtitle_downloads: list[Subtitle] = []
        self.download_number = 1
        self.download_index_size = len(subtitles)
        self.subtitles = subtitles
        self.scrollbar = ttk.Scrollbar(frame_right, orient="vertical", style="Vertical.TScrollbar")
        self.sub_listbox = tk.Listbox(
            frame_left,
            height=36,
            bg=cfg.color.default_bg,
            fg=cfg.color.light_grey,
            font=cfg.font.cas8b,
            bd=0,
            border=0,
            borderwidth=0,
            highlightthickness=0,
            activestyle="none",
            yscrollcommand=self.scrollbar.set,
        )
        self.sub_listbox.pack(expand=True, fill="both")
        if self.subtitles is not None:
            self.fill_listbox()
        self.scrollbar.pack(expand=True, fill="y")
        self.scrollbar.config(command=self.sub_listbox.yview)
        if not self.subtitles:
            self.nothing_label = tk.Label(
                self,
                text="It's very empty...\n\n:(",
                font=cfg.font.cas20b,
                fg=cfg.color.default_fg,
                bg=cfg.color.default_bg,
                anchor="center",
                justify="center",
            )
            self.nothing_label.place(x=cfg.size.height // 2, y=cfg.size.width // 4, anchor="center")

    def fill_listbox(self) -> None:
        accept_threshold = io_toml.load_toml_value(FILE_PATHS.config, "subtitle_filters.accept_threshold")
        automatic_downloads = io_toml.load_toml_value(FILE_PATHS.config, "download_manager.automatic_downloads")
        self.listbox_index: dict[int, Subtitle] = {}
        for enum, subtitle in enumerate(self.subtitles):
            self.sub_listbox.insert(tk.END, f"{subtitle.precentage_result}% {subtitle.subtitle_name}\n")
            if subtitle.precentage_result == accept_threshold and not automatic_downloads:
                self.downloaded_subtitle.append(subtitle)
                self.download_number += 1
                self.update_text(enum, "✓", subtitle, cfg.color.green)
            self.sub_listbox.bind("<ButtonPress-1>", self.mouse_b1_press)
            self.listbox_index[enum] = subtitle

    def mouse_b1_press(self, event) -> None:
        self.sub_listbox.unbind("<ButtonPress-1>")
        self.sub_listbox.bind("<<ListboxSelect>>", self.select_subtitle)

    def select_subtitle(self, event) -> None:
        self.sub_listbox.unbind("<<ListboxSelect>>")
        _selection = self.sub_listbox.curselection()
        selection = _selection[0]
        subtitle = self.listbox_index[selection]
        if subtitle in (self.downloaded_subtitle or self.failed_subtitle_downloads):
            self.sub_listbox.bind("<ButtonPress-1>", self.mouse_b1_press)
            return
        if subtitle.provider_name == "subsource":
            subsource_api = subsource.GetDownloadUrl()
            download_url = subsource_api.get_url(subtitle)
            if not download_url:
                self.update_text(selection, "⨯", subtitle, cfg.color.red)
            else:
                subtitle.download_url = download_url
                subtitle.request_data = {}
        self.update_text(selection, "⊙", subtitle, cfg.color.orange)
        self.sub_listbox.bind("<ButtonRelease-1>", lambda event: self.download(event, subtitle, selection))

    def download(self, event, subtitle: Subtitle, selection: int) -> None:
        self.sub_listbox.unbind("<ButtonRelease-1>")
        try:
            if string_parser.valid_filename(subtitle.subtitle_name):
                subtitle.subtitle_name = string_parser.fix_filename(subtitle.subtitle_name)
            io_file_system.download_subtitle(subtitle, self.download_number, self.download_index_size)
            io_file_system.extract_files_in_dir(VIDEO_FILE.tmp_dir, VIDEO_FILE.subs_dir)
            zip_archive = (
                VIDEO_FILE.tmp_dir / f"{subtitle.provider_name}_{subtitle.subtitle_name}_{self.download_number}.zip"
            )
            zip_archive.unlink()
            self.update_text(selection, "✓", subtitle, cfg.color.green)
            self.download_number += 1
            self.download_index_size += 1
            self.downloaded_subtitle.append(subtitle)
        except Exception as e:
            log.stdout(str(e), level="error")
            self.update_text(selection, "⨯", subtitle, cfg.color.red)
            self.failed_subtitle_downloads.append(subtitle)
        finally:
            self.sub_listbox.bind("<ButtonPress-1>", self.mouse_b1_press)

    def update_text(self, selection: int, symbol: str, subtitle: Subtitle, color: str) -> None:
        self.sub_listbox.delete(int(selection))
        self.sub_listbox.insert(int(selection), f"{symbol} {subtitle.subtitle_name}")
        self.sub_listbox.itemconfig(int(selection), {"fg": color})
