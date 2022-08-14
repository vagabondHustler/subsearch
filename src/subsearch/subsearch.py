import ctypes
import os
import sys
import time

from data import __version__
from gui import widget_download, widget_settings
from scraper import opensubtitles, subscene
from utils import (
    current_user,
    file_manager,
    file_parser,
    local_paths,
    log,
    raw_config,
    raw_registry,
)


class SubSearch:
    def __init__(self) -> None:
        self.start = time.perf_counter()
        ctypes.windll.kernel32.SetConsoleTitleW(f"SubSearch - {__version__}")
        self.run_subsearch = True
        self.file_path = None
        self.full_filename = None
        self.file_exist = False
        self.show_terminal = raw_config.get("show_terminal")
        if current_user.got_key() is False:
            raw_config.set_default_json()
            raw_registry.add_context_menu()
        if current_user.check_is_exe():
            raw_config.set_json("show_terminal", False)
        for ext in raw_config.get("file_ext"):
            if sys.argv[-1].endswith(ext):
                self.file_exist = True
                file_full_path = sys.argv[-1]
                index = file_full_path.rfind("\\")
                self.file_path = file_full_path[0:index]
                self.full_filename = file_full_path[index + 1 :]
                os.chdir(self.file_path)
                break

        self.lang, self.lang_abbr = raw_config.get("language")
        self.hi = raw_config.get("hearing_impaired")
        self.pct = raw_config.get("percentage")
        self.show_dl_window = raw_config.get("show_download_window")
        if self.file_exist:
            self.video_filename, self.video_file_ext = self.full_filename.rsplit(".", 1)
            self.file_hash = file_manager.get_hash(self.full_filename)
            self.param = file_parser.get_parameters(self.video_filename, self.file_hash, self.lang_abbr)
            log.parameters(self.param, self.lang, self.lang_abbr, self.hi, self.pct)

        if self.file_exist is False:
            widget_settings.show_widget()

    def opensubtitles_scrape(self):
        if self.file_exist:
            log.output("")
            log.output("[Searching on opensubtitles]")
            self.scrape_opensubtitles = opensubtitles.scrape(self.param, self.lang, self.hi)

    def subscene_scrape(self):
        if self.file_exist:
            log.output("")
            log.output("[Searching on subscene]")
            self.scrape_subscene = subscene.scrape(
                self.param, self.lang, self.lang_abbr, self.hi, self.pct, self.show_dl_window
            )

    def procsess_files(self):
        if self.file_exist:
            if self.scrape_opensubtitles is not None:
                log.output("")
                log.output("[Downloading from Opensubtitles]")
                for item in self.scrape_opensubtitles:
                    file_manager.download_zip_auto(item)

            if self.scrape_subscene[0] is not None:
                log.output("")
                log.output("[Downloading from Subscene]")
                for item in self.scrape_subscene:
                    file_manager.download_zip_auto(item)

            if self.scrape_opensubtitles is None and self.scrape_subscene is None:
                dl_data = f"{local_paths.cwd()}\\__subsearch__dl_data.tmp"
                if self.show_dl_window is True and os.path.exists(dl_data):
                    widget_download.show_widget()
                    file_manager.clean_up(local_paths.cwd(), dl_data)
                    if local_paths.cwd() != local_paths.get_path("root"):
                        file_manager.copy_log(local_paths.get_path("root"), local_paths.cwd())

            log.output("")
            log.output("[Procsessing files]")
            file_manager.extract_zips(local_paths.cwd(), ".zip")
            file_manager.clean_up(local_paths.cwd(), ".zip")
            file_manager.clean_up(local_paths.cwd(), ").nfo")
            file_manager.rename_best_match(f"{self.param.release}.srt", local_paths.cwd(), ".srt")

    def _exit_(self):
        if local_paths.cwd() != local_paths.get_path("root"):
            file_manager.copy_log(local_paths.get_path("root"), local_paths.cwd())
        elapsed = time.perf_counter() - self.start
        log.output("")
        log.output(f"Finished in {elapsed} seconds")
        if self.show_terminal is True and current_user.check_is_exe() is False:
            input("Press Enter to exit...")


def main():
    ss = SubSearch()
    ss.opensubtitles_scrape()
    ss.subscene_scrape()
    ss.procsess_files()
    ss._exit_()


if __name__ == "__main__":
    main()
