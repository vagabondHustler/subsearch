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

    def start_app(self) -> None:
        self.subsearch_core.init_search(
            self.subsearch_core.opensubtitles,
            self.subsearch_core.yifysubtitles,
            self.subsearch_core.subsource,
        )
        self.subsearch_core.download_files()
        self.subsearch_core.download_manager()
        self.subsearch_core.extract_files()
        self.subsearch_core.subtitle_post_processing()
        self.subsearch_core.clean_up()

    def exit_app(self) -> None:
        self.subsearch_core.core_on_exit()


@decorators.apply_mutex
def main() -> None:
    subsearch = Subsearch()
    subsearch.start_app()
    subsearch.exit_app()


if __name__ == "__main__":
    main()
