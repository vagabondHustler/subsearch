import ctypes
import os
import time

from data import __version__, __video_directory__, __video_name__, __video_path__
from gui import widget_download, widget_settings
from scraper import opensubtitles, subscene
from utils import current_user, file_manager, file_parser, log, raw_config, raw_registry


class SubSearch:
    def __init__(self) -> None:
        self.start = time.perf_counter()
        ctypes.windll.kernel32.SetConsoleTitleW(f"SubSearch - {__version__}")
        if current_user.got_key() is False:
            raw_config.set_default_json()
            raw_registry.add_context_menu()
        self.show_terminal = False if current_user.check_is_exe() else raw_config.get("show_terminal")
        self.file_exist = True if __video_name__ is not None else False
        self.lang, self.lang_abbr = raw_config.get("language")
        self.hi = raw_config.get("hearing_impaired")
        self.pct = raw_config.get("percentage")
        self.show_dl_window = raw_config.get("show_download_window")
        if self.file_exist:
            self.file_hash = file_manager.get_hash(__video_path__)
            self.param = file_parser.get_parameters(__video_name__, self.file_hash, self.lang_abbr)
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
                dl_data = f"{__video_directory__}\\__subsearch__dl_data.tmp"
                if self.show_dl_window is True and os.path.exists(dl_data):
                    widget_download.show_widget()
                    file_manager.clean_up(__video_directory__, dl_data)

            log.output("")
            log.output("[Procsessing files]")
            file_manager.extract_zips(__video_directory__, ".zip")
            file_manager.clean_up(__video_directory__, ".zip")
            file_manager.clean_up(__video_directory__, ").nfo")
            file_manager.rename_best_match(f"{self.param.release}.srt", __video_directory__, ".srt")

    def _exit_(self):
        elapsed = time.perf_counter() - self.start
        log.output("")
        log.output(f"Finished in {elapsed} seconds")
        try:
            while self.show_terminal and current_user.check_is_exe() is False:
                print("\nCtrl + c to exit")
                time.sleep(900)
        except KeyboardInterrupt:
            pass


def main():
    ss = SubSearch()
    ss.opensubtitles_scrape()
    ss.subscene_scrape()
    ss.procsess_files()
    ss._exit_()


if __name__ == "__main__":
    main()
