import sys
import time
from pathlib import Path
from threading import Thread

from subsearch import core
from subsearch.data import __guid__
from subsearch.data.constants import FILE_PATHS
from subsearch.utils import decorators, io_log, io_toml

PREF_COUNTER = time.perf_counter()
PACKAGEPATH = Path(__file__).resolve().parent.as_posix()
HOMEPATH = Path(PACKAGEPATH).parent.as_posix()
sys.path.append(HOMEPATH)
sys.path.append(PACKAGEPATH)


class Subsearch:
    def __init__(self) -> None:
        self.subsearch_core = core.SubsearchCore(PREF_COUNTER)

    def thread_executor(self, *args) -> None:
        provider_threads = {}
        for provider in args:
            provider_threads[provider] = Thread(target=provider)

        for thread in provider_threads.values():
            thread.start()

        for thread in provider_threads.values():
            thread.join()

    def search_for_subtitles(self) -> None:
        providers = [self.subsearch_core.subscene, self.subsearch_core.opensubtitles, self.subsearch_core.yifysubtitles]

        if io_toml.load_toml_value(FILE_PATHS.config, "misc.multithreading"):
            self.thread_executor(*providers)

        else:
            for provider in providers:
                provider()

    def provider_opensubtitles(self) -> None:
        self.subsearch_core.opensubtitles()

    def provider_subscene(self) -> None:
        self.subsearch_core.subscene()

    def provider_yifysubtitles(self) -> None:
        self.subsearch_core.yifysubtitles()

    def process_files(self) -> None:
        self.subsearch_core.download_files()
        self.subsearch_core.manual_download()
        self.subsearch_core.extract_files()
        self.subsearch_core.subtitle_post_processing()
        self.subsearch_core.clean_up()

    def on_exit(self) -> None:
        self.subsearch_core.core_on_exit()


@decorators.apply_mutex
def main() -> None:
    app = Subsearch()
    app.search_for_subtitles()
    app.process_files()
    app.on_exit()


def custom_excepthook(exctype, value, traceback):
    io_log.Logger().debug_logger.error(value, exc_info=(exctype, value, traceback))
    sys.__excepthook__(exctype, value, traceback)


if __name__ == "__main__":
    sys.excepthook = custom_excepthook
    main()
