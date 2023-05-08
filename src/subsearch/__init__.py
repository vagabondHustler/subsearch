import sys
from pathlib import Path
from threading import Thread

from subsearch import core
from subsearch.data import __guid__
from subsearch.gui import tab_manager
from subsearch.utils import io_json, io_winreg, mutex_synchronizer

PACKAGEPATH = Path(__file__).resolve().parent.as_posix()
HOMEPATH = Path(PACKAGEPATH).parent.as_posix()
sys.path.append(HOMEPATH)
sys.path.append(PACKAGEPATH)


class Subsearch(core.AppSteps):
    def __init__(self) -> None:
        """
        Setup and gather all available parameters
        """
        core.AppSteps.__init__(self)

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
        if io_json.get_json_key("use_threading"):
            self.thread_executor(
                self._provider_subscene,
                self._provider_opensubtitles,
                self._provider_yifysubtitles,
            )
        else:
            self._provider_subscene()
            self._provider_opensubtitles()
            self._provider_yifysubtitles()

    def provider_opensubtitles(self) -> None:
        """
        Search for subtitles on opensubtitles
        """
        self._provider_opensubtitles()

    def provider_subscene(self) -> None:
        """
        Search for subtitles on subscene
        """
        self._provider_subscene()

    def provider_yifysubtitles(self) -> None:
        """
        Search for subtitles on yifysubtitles
        """
        self._provider_yifysubtitles()

    def process_files(self) -> None:
        """
        Download zip files containing the .srt files, extract, rename and clean up tmp files
        """
        self._download_files()
        self._not_downloaded()
        self._extract_zip_files()
        self._clean_up()

    def pre_exit(self) -> None:
        """
        Stop pref counter, log elapsed time and keep the terminal open if show_terminal is True
        """
        self._pre_exit()


def console() -> None:
    r"""
    Usages: subsearch [OPTIONS]

    Options:
        --settings [lang, search, app, dl]      Open the GUI settings menu
                                                    ang: opens tab with available languages
                                                    search: opens tab with settings such as available providers
                                                    app: opens tab with app settings
                                                    dl: opens tab for subtitles not downloaded

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
                tab_manager.open_tab("language")
            elif sys.argv[num + 1] == "search":
                sys.argv.pop(num), sys.argv.pop(num)
                tab_manager.open_tab("search")
            elif sys.argv[num + 1] == "app":
                sys.argv.pop(num), sys.argv.pop(num)
                tab_manager.open_tab("settings")
            elif sys.argv[num + 1] == "dl":
                sys.argv.pop(num), sys.argv.pop(num)
                tab_manager.open_tab("download")

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


@mutex_synchronizer.synchronized(__guid__)
def main() -> None:
    for i in sys.argv:
        if i.startswith("--"):
            console()
            return None

    app = Subsearch()
    app.search_for_subtitles()
    app.process_files()
    app.pre_exit()


if __name__ == "__main__":
    main()
