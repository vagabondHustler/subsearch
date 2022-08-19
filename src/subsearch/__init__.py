import ctypes
import os
import sys
import time

from subsearch.data import (
    __version__,
    __video_directory__,
    __video_name__,
    __video_path__,
)
from subsearch.gui import widget_download, widget_settings
from subsearch.scraper import opensubtitles, subscene
from subsearch.utils import (
    current_user,
    file_manager,
    log,
    raw_config,
    raw_registry,
    string_parser,
)

PACKAGEPATH = os.path.abspath(os.path.dirname(__file__))
HOMEPATH = os.path.dirname(PACKAGEPATH)
sys.path.append(HOMEPATH)
sys.path.append(PACKAGEPATH)


class SubSearch:
    def __init__(self) -> None:
        """
        Setup and gather all available parameters
        """
        self.start = time.perf_counter()
        ctypes.windll.kernel32.SetConsoleTitleW(f"SubSearch - {__version__}")
        if current_user.got_key() is False:
            raw_config.set_default_json()
            raw_registry.add_context_menu()
        self.show_terminal = False if current_user.check_is_exe() else raw_config.get("show_terminal")
        self.file_exist = True if __video_name__ is not None else False
        self.lang, self.lang_code2 = raw_config.get("language")
        self.hi = raw_config.get("hearing_impaired")
        self.pct = raw_config.get("percentage")
        self.show_dl_win = raw_config.get("show_download_window")
        if self.file_exist:
            file_hash = file_manager.get_hash(__video_path__)
            self.param = string_parser.get_parameters(__video_name__, file_hash, self.lang, self.lang_code2)
            log.parameters(self.param, self.lang, self.lang_code2, self.hi, self.pct)
            if " " in __video_name__:
                log.output("[Warning: Filename contains spaces]")
        if self.file_exist is False:
            widget_settings.show_widget()

    def opensubtitles_scrape(self) -> None:
        """
        Scrape on opensubtitles by filehash
        """
        if self.file_exist:
            log.output("")
            log.output("[Searching on opensubtitles]")
            self.opensubtitles = opensubtitles.scrape(self.param, self.lang, self.hi)

    def subscene_scrape(self) -> None:
        """
        Scrape subscene from parsing filename of the video
        """
        if self.file_exist:
            log.output("")
            log.output("[Searching on subscene]")
            self.subscene = subscene.scrape(self.param, self.lang, self.lang_code2, self.hi, self.pct, self.show_dl_win)

    def process_files(self) -> None:
        """
        Download zip files containing the .srt files, extract, rename and clean up tmp files
        """
        if self.file_exist is False:
            return None

        if self.opensubtitles is not None:
            log.output("")
            log.output("[Downloading from Opensubtitles]")
            for item in self.opensubtitles:
                file_manager.download_zip(item)

        if self.subscene is not None:
            log.output("")
            log.output("[Downloading from Subscene]")
            for item in self.subscene:
                file_manager.download_zip(item)

        if self.opensubtitles is None and self.subscene is None:
            dl_data = f"{__video_directory__}\\__subsearch__dl_data.tmp"
            if self.show_dl_win is True and os.path.exists(dl_data):
                widget_download.show_widget()
                file_manager.clean_up(__video_directory__, dl_data)

        log.output("")
        log.output("[Procsessing files]")
        file_manager.extract_zips(__video_directory__, ".zip")
        file_manager.clean_up(__video_directory__, ".zip")
        file_manager.clean_up(__video_directory__, ").nfo")
        file_manager.rename_best_match(f"{self.param.release}.srt", __video_directory__, ".srt")

    def end(self) -> None:
        """
        Stop pref counter, log elapsed time and keep the terminal open if show_terminal is True
        """
        elapsed = time.perf_counter() - self.start
        log.output("")
        log.output(f"Finished in {elapsed} seconds")

        if self.show_terminal and current_user.check_is_exe() is False:
            input("Ctrl + c or Enter to exit")


def con() -> None:
    r"""
    Usages: subsearch [OPTIONS]

    Options:
        --settings                                  Open the GUI settings menu

        --registry-key [add, del]                   Edit the registry
                                                    add: adds the context menu  / replaces the context menu with default values
                                                    del: deletes the context menu
                                                    e.g: subsearch --registry-key add

        --help                                      Prints usage information
    """
    if sys.argv[-1].endswith("subsearch"):
        print(con.__doc__)
        return
    else:
        for num, arg in enumerate(sys.argv[1:], 1):
            if arg.startswith("--settings"):
                sys.argv.pop(num)  # pop settings argument
                widget_settings.show_widget()
                break
            elif arg.startswith("--registry-key") or arg.startswith("--add-key"):
                if sys.argv[num + 1] == "add":
                    sys.argv.pop(num)  # pop registry argument
                    sys.argv.pop(num)  # pop add argument
                    raw_registry.add_context_menu()
                    break
                elif sys.argv[num + 1] == "del":
                    sys.argv.pop(num)  # pop registry argument
                    sys.argv.pop(num)  # pop del argument
                    raw_registry.remove_context_menu()
                    break
            elif arg.startswith("--help"):
                sys.argv.pop(num)  # pop help argument
                print(con.__doc__)
                break
            elif len(sys.argv[1:]) == num:
                print("Invalid argument")
                print(con.__doc__)


def main() -> None:
    for i in sys.argv:
        if i.startswith("--"):
            con()
            return None

    ss = SubSearch()
    ss.opensubtitles_scrape()
    ss.subscene_scrape()
    ss.process_files()
    ss.end()


if __name__ == "__main__":
    main()
