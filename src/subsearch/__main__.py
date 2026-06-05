from subsearch import PREF_COUNTER
from subsearch.decorators import process_guard
from subsearch.core.pipeline import SearchPipeline


class Subsearch:
    def __init__(self) -> None:
        self.pipeline = SearchPipeline(PREF_COUNTER)

    def start_app(self) -> None:
        self.pipeline.init_search(
            self.pipeline.opensubtitles,
            self.pipeline.yifysubtitles,
            self.pipeline.subsource,
        )
        self.pipeline.download_files()
        self.pipeline.download_manager()
        self.pipeline.subtitle_post_processing()
        self.pipeline.run_provider_diagnostics()
        self.pipeline.clean_up()

    def exit_app(self) -> None:
        self.pipeline.on_exit()


@process_guard.apply_mutex
def main() -> None:
    subsearch = Subsearch()
    subsearch.start_app()
    subsearch.exit_app()


if __name__ == "__main__":
    main()
