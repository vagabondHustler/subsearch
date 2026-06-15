from subsearch import PREF_COUNTER
from subsearch.core.flows import create_flow
from subsearch.core.pipeline import SearchPipeline
from subsearch.decorators import process_guard


class Subsearch:
    def __init__(self) -> None:
        self.pipeline = SearchPipeline(PREF_COUNTER)
        self.flow = create_flow(self.pipeline)

    def start_app(self) -> None:
        self.flow.run()

    def exit_app(self) -> None:
        self.pipeline.on_exit()


@process_guard.apply_mutex
def main() -> None:
    subsearch = Subsearch()
    try:
        subsearch.start_app()
    except KeyboardInterrupt:
        pass
    finally:
        subsearch.exit_app()


if __name__ == "__main__":
    main()
