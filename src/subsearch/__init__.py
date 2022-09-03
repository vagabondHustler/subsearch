import ctypes
import os
import sys
import time

from subsearch.data import __version__, __video__
from subsearch.gui import widget_menu
from subsearch.providers import opensubtitles, subscene
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


class Subsearch:
    def __init__(self) -> None:
        """
        Setup and gather all available parameters
        """
        self.start = time.perf_counter()
        ctypes.windll.kernel32.SetConsoleTitleW(f"SubSearch - {__version__}")
        if current_user.got_key() is False:
            raw_config.set_default_json()
            raw_registry.add_context_menu()
        self.show_terminal = False if current_user.check_is_exe() else raw_config.get_config_key("show_terminal")
        self.providers = raw_config.get_config_key("providers")

        self.file_exist = True if __video__.name is not None else False
        self.current_language = raw_config.get_config_key("current_language")
        self.languages = raw_config.get_config_key("languages")
        self.hi = raw_config.get_config_key("hearing_impaired")
        self.pct = raw_config.get_config_key("percentage")
        self.show_dl_win = raw_config.get_config_key("show_download_window")
        self.user_parameters = raw_config.UserParameters(
            current_language=self.current_language,
            hearing_impaired=self.hi,
            pct=self.pct,
            show_dl_window=self.show_dl_win,
        )
        if self.file_exist:
            self.file_hash = file_manager.get_hash(__video__.path)
            self.parameters = string_parser.get_parameters(
                __video__.name, self.file_hash, self.current_language, self.languages
            )
            log.parameters(self.parameters, self.user_parameters)
            if " " in __video__.name:
                log.output("[Warning: Filename contains spaces]")
        if self.file_exist is False:
            widget_menu.open_tab("search")
            return None

    def opensubtitles_scrape(self) -> None:
        """
        Scrape on opensubtitles by filehash
        """
        if self.languages[self.current_language] == "N/A":
            log.output("\n[Searching on opensubtitles]")
            log.output(f"{self.current_language} not supported on opensubtitles\n")
            self.opensubtitles_hash = None
            self.opensubtitles_rss = None
            self.opensubtitles_sorted_list = []
            return
        if self.file_exist and (self.providers["opensubtitles_hash"] or self.providers["opensubtitles_rss"]):
            _opensubtitles = opensubtitles.OpenSubtitles(self.parameters, self.user_parameters)
            if self.providers["opensubtitles_hash"] and self.file_hash is not None:
                log.output("\n[Searching on opensubtitles - hash]")
                self.opensubtitles_hash = _opensubtitles.parse_hash()
            if self.providers["opensubtitles_rss"]:
                log.output("\n[Searching on opensubtitles - rss]")
                self.opensubtitles_rss = _opensubtitles.parse_rss()
            self.opensubtitles_sorted_list = _opensubtitles.sorted_list()

    def subscene_scrape(self) -> None:
        """
        Scrape subscene from parsing filename of the video
        """
        if self.file_exist and self.providers["subscene"]:
            log.output("\n[Searching on subscene - title]")
            _subscene = subscene.Subscene(self.parameters, self.user_parameters)
            self.subscene = _subscene.parse()
            self.subscene_sorted_list = _subscene.sorted_list()
        else:
            self.subscene = None

    def process_files(self) -> None:
        """
        Download zip files containing the .srt files, extract, rename and clean up tmp files
        """
        os_hash_dls = 0
        os_rss_dls = 0
        ss_dls = 0
        if self.file_exist is False:
            return None

        if self.providers["opensubtitles_hash"] and self.opensubtitles_hash is not None:
            log.output("\n[Downloading from opensubtitles - hash]")
            for item in self.opensubtitles_hash:
                os_hash_dls = file_manager.download_subtitle(item)
                log.output("\n")

        if self.providers["opensubtitles_rss"] and self.opensubtitles_rss is not None:
            log.output("\n[Downloading from opensubtitles - rss]")
            for item in self.opensubtitles_rss:
                os_rss_dls = file_manager.download_subtitle(item)

        if self.providers["subscene"] and self.subscene is not None:
            log.output("\n[Downloading from subscene]")
            for item in self.subscene:
                ss_dls = file_manager.download_subtitle(item)

        total_dls = os_hash_dls + os_rss_dls + ss_dls
        if self.show_dl_win and total_dls == 0:
            not_downloaded = list(self.opensubtitles_sorted_list)
            not_downloaded.extend(x for x in self.subscene_sorted_list if x not in not_downloaded)
            not_downloaded.sort(key=lambda x: x[0], reverse=True)
            if len(not_downloaded) > 0:
                tmp_file = file_manager.write_not_downloaded_tmp(__video__.directory, not_downloaded)
                widget_menu.open_tab("download")
                file_manager.clean_up(__video__.directory, tmp_file)

        log.output("\n[Procsessing files]")
        file_manager.extract_files(__video__.directory, ".zip")
        file_manager.clean_up(__video__.directory, ".zip")
        file_manager.clean_up(__video__.directory, ").nfo")
        file_manager.rename_best_match(f"{self.parameters.release}.srt", __video__.directory, ".srt")

    def end(self) -> None:
        """
        Stop pref counter, log elapsed time and keep the terminal open if show_terminal is True
        """
        elapsed = time.perf_counter() - self.start
        log.output(f"\nFinished in {elapsed} seconds")

        if self.show_terminal and current_user.check_is_exe() is False:
            try:
                input("Ctrl + c or Enter to exit")
            except KeyboardInterrupt:
                pass


def con() -> None:
    r"""
    Usages: subsearch [OPTIONS]

    Options:
        --settings [lang, search, app, dl]        Open the GUI settings menu
                                                            lang: opens tab with available languages
                                                            search: opens tab with settings such as available providers
                                                            app: opens tab with app settings
                                                            dl: opens tab for subtitles not downloaded

        --registry-key [add, del]                           Edit the registry
                                                            add: adds the context menu  / replaces the context menu with default values
                                                            del: deletes the context menu
                                                            e.g: subsearch --registry-key add

        --help                                              Prints usage information
    """

    for num, arg in enumerate(sys.argv[1:], 1):
        if arg.startswith("--settings"):
            if sys.argv[num + 1] == "lang":
                sys.argv.pop(num), sys.argv.pop(num)  # pop arguments
                widget_menu.open_tab("language")
            elif sys.argv[num + 1] == "search":
                sys.argv.pop(num), sys.argv.pop(num)  # pop arguments
                widget_menu.open_tab("search")
            elif sys.argv[num + 1] == "app":
                sys.argv.pop(num), sys.argv.pop(num)  # pop arguments
                widget_menu.open_tab("settings")
            elif sys.argv[num + 1] == "dl":
                sys.argv.pop(num), sys.argv.pop(num)  # pop arguments
                widget_menu.open_tab("download")

            break
        elif arg.startswith("--registry-key") or arg.startswith("--add-key"):
            if sys.argv[num + 1] == "add":
                sys.argv.pop(num), sys.argv.pop(num)  # pop arguments
                raw_registry.add_context_menu()
                break
            elif sys.argv[num + 1] == "del":
                sys.argv.pop(num), sys.argv.pop(num)  # pop arguments
                raw_registry.remove_context_menu()
                break
        elif arg.startswith("--help"):
            sys.argv.pop(num)  # pop argument
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

    step = Subsearch()
    step.opensubtitles_scrape()
    step.subscene_scrape()
    step.process_files()
    step.end()


if __name__ == "__main__":
    main()
