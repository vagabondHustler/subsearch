import sys
import time
from pathlib import Path
from threading import Thread

from subsearch import core
from subsearch.data import __guid__
from subsearch.data.constants import FILE_PATHS
from subsearch.gui import screen_manager
from subsearch.utils import decorators, io_json, io_log, io_winreg

PREF_COUNTER = time.perf_counter()
PACKAGEPATH = Path(__file__).resolve().parent.as_posix()
HOMEPATH = Path(PACKAGEPATH).parent.as_posix()
sys.path.append(HOMEPATH)
sys.path.append(PACKAGEPATH)


class Subsearch:
    def __init__(self) -> None:
        """
        Setup and gather all available parameters
        """
        self.subsearch_core = core.SubsearchCore(PREF_COUNTER)
    

    def thread_executor(self, *args) -> None:
        """
        Search for subtitles with active providers concurrently.
        """
        provider_threads = {}
        for provider in args:
            provider_threads[provider] = Thread(target=provider)

        for thread in provider_threads.values():
            thread.start()

        for thread in provider_threads.values():
            thread.join()

    def search_for_subtitles(self) -> None:
        """
        Runs a search with all active providers, either concurrently or separately.
        """
        if io_json.get_json_key("use_threading", FILE_PATHS.subsearch_config):
            self.thread_executor(
                self.subsearch_core.subscene,
                self.subsearch_core.opensubtitles,
                self.subsearch_core.yifysubtitles,
            )
        else:
            self.subsearch_core.subscene()
            self.subsearch_core.opensubtitles()
            self.subsearch_core.yifysubtitles()

    def provider_opensubtitles(self) -> None:
        """
        Search for subtitles on opensubtitles
        """
        self.subsearch_core.opensubtitles()

    def provider_subscene(self) -> None:
        """
        Search for subtitles on subscene
        """
        self.subsearch_core.subscene()

    def provider_yifysubtitles(self) -> None:
        """
        Search for subtitles on yifysubtitles
        """
        self.subsearch_core.yifysubtitles()

    def process_files(self) -> None:
        """
        Download zip files containing the .srt files, extract, rename and clean up tmp files
        """
        self.subsearch_core.download_files()
        self.subsearch_core.manual_download()
        self.subsearch_core.extract_files()
        self.subsearch_core.autoload_rename()
        self.subsearch_core.autoload_move()
        self.subsearch_core.clean_up()

    def on_exit(self) -> None:
        """
        Stop pref counter, log elapsed time and keep the terminal open if show_terminal is True
        """
        self.subsearch_core.core_on_exit()


def console() -> None:
    r"""
    Usages: subsearch [OPTIONS]

    Options:
        --settings [lang, search, app, dl]      Open the GUI settings menu
                                                    ang: opens screen with available languages
                                                    search: opens screen with settings such as available providers
                                                    app: opens screen with app settings
                                                    dl: opens screen for subtitles not downloaded

        --registry-key [add, del]               Edit the registry
                                                    add: adds the context menu  / replaces the context menu with default values
                                                    del: deletes the context menu
                                                    e.g: subsearch --registry-key add

        --help                                  Prints usage information
    """

    for num, arg in enumerate(sys.argv[1:], 1):
        if arg.startswith("--settings"):
            if sys.argv[num + 1] == "lang":
                sys.argv.pop(num), sys.argv.pop(num)
                screen_manager.open_screen("language")
            elif sys.argv[num + 1] == "search":
                sys.argv.pop(num), sys.argv.pop(num)
                screen_manager.open_screen("search")
            elif sys.argv[num + 1] == "app":
                sys.argv.pop(num), sys.argv.pop(num)
                screen_manager.open_screen("settings")
            elif sys.argv[num + 1] == "dl":
                sys.argv.pop(num), sys.argv.pop(num)
                screen_manager.open_screen("download")

            break
        elif arg.startswith("--registry-key") or arg.startswith("--add-key"):
            if sys.argv[num + 1] == "add":
                sys.argv.pop(num), sys.argv.pop(num)
                io_winreg.add_context_menu()
                break
            elif sys.argv[num + 1] == "del":
                sys.argv.pop(num), sys.argv.pop(num)
                io_winreg.remove_context_menu()
                break
        elif arg.startswith("--help"):
            sys.argv.pop(num)  # pop argument
            print(console.__doc__)
            break
        elif len(sys.argv[1:]) == num:
            print("Invalid argument")
            print(console.__doc__)


@decorators.apply_mutex
def main() -> None:
    for i in sys.argv:
        if i.startswith("--"):
            console()
            return None

    app = Subsearch()
    app.search_for_subtitles()
    app.process_files()
    app.on_exit()


def custom_excepthook(exctype, value, traceback):
    io_log._logger.debug_logger.error(value, exc_info=(exctype, value, traceback))
    sys.__excepthook__(exctype, value, traceback)


if __name__ == "__main__":
    sys.excepthook = custom_excepthook
    main()
