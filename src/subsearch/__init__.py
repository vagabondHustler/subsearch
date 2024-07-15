import sys
import time
from pathlib import Path

from subsearch import core
from subsearch.globals import decorators

PREF_COUNTER = time.perf_counter()
PACKAGE_PATH = Path(__file__).resolve().parent.as_posix()
HOME_PATH = Path(PACKAGE_PATH).parent.as_posix()
sys.path.append(HOME_PATH)
sys.path.append(PACKAGE_PATH)


class Subsearch:
    def __init__(self) -> None:
        self.subsearch_core = core.SubsearchCore(PREF_COUNTER)

    def search_for_subtitles(self) -> None:
        self.subsearch_core.init_search(
            self.provider_opensubtitles,
            self.provider_yifysubtitles,
            self.provider_subsource,
        )

    def provider_opensubtitles(self) -> None:
        self.subsearch_core.opensubtitles()


    def provider_yifysubtitles(self) -> None:
        self.subsearch_core.yifysubtitles()
        
    def provider_subsource(self) -> None:
        self.subsearch_core.subsource()

    def process_files(self) -> None:
        self.subsearch_core.download_files()
        self.subsearch_core.download_manager()
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


if __name__ == "__main__":
    main()
