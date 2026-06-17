import sys

from subsearch import PREF_COUNTER, set_crash_notifier
from subsearch.core.flows import create_flow
from subsearch.core.pipeline import SearchPipeline
from subsearch.decorators import process_guard
from subsearch.runtime.models import AppMode

 
class Subsearch:
    def __init__(self) -> None:
        self.pipeline = SearchPipeline(PREF_COUNTER)
        self.flow = create_flow(self.pipeline)
        set_crash_notifier(self._notify_crash)

    def _notify_crash(self) -> None:
        bootstrap = self.pipeline.bootstrap
        if bootstrap.app_mode is not AppMode.SEARCH_AUTOMATIC:
            return
        if not bootstrap.app_config.system_tray:
            return
        bootstrap.system_tray.display_toast("Subsearch crashed", "See crash.log for details")

    def start_app(self) -> None:
        self.flow.run()

    def exit_app(self) -> None:
        self.pipeline.on_exit()


def _force_utf8_console() -> None:
    # prevent non-cp1252 glyphs crash on windows
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8")


@process_guard.apply_mutex
def main() -> None:
    _force_utf8_console()
    subsearch = Subsearch()
    try:
        subsearch.start_app()
    except KeyboardInterrupt:
        pass
    finally:
        subsearch.exit_app()


if __name__ == "__main__":
    main()
