import sys

from subsearch import PERF_COUNTER, set_crash_notifier
from subsearch.core.pipeline import SearchPipeline
from subsearch.decorators import process_guard
from subsearch.runtime import recorder
from subsearch.runtime.config import FILE_PATHS
from subsearch.runtime.models import AppMode
from subsearch.runtime.recorder import RecorderConfig
from subsearch.ui.services.console_bridge import CONSOLE_BRIDGE


class Subsearch:
    def __init__(self) -> None:
        self.pipeline = SearchPipeline(PERF_COUNTER)

    def _notify_crash(self) -> None:
        bootstrap = self.pipeline.bootstrap
        if bootstrap.app_mode is not AppMode.SEARCH_AUTOMATIC:
            return
        if not bootstrap.app_config.system_tray:
            return
        bootstrap.system_tray.display_toast("Subsearch crashed", "See crash.log for details")

    def _start_app(self) -> None:
        self.pipeline.run()

    def _exit_app(self) -> None:
        self.pipeline.on_exit()

    def run(self) -> None:
        try:
            self._start_app()
        except KeyboardInterrupt:
            pass
        finally:
            self._exit_app()


def _force_utf8_console() -> None:
    # prevent non-cp1252 glyphs crash on windows
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        reconfigure(encoding="utf-8")


def _start_recorder() -> None:
    config = RecorderConfig(
        log_file_path=FILE_PATHS.log,
        crash_file_path=FILE_PATHS.crash,
        console_outputs=(CONSOLE_BRIDGE.emit,),
        start_perf_counter=PERF_COUNTER,
    )
    recorder.init(config)


def _init_runtime() -> None:
    _force_utf8_console()
    _start_recorder()


@process_guard.apply_mutex
def main() -> None:
    _init_runtime()
    app = Subsearch()
    set_crash_notifier(app._notify_crash)
    app.run()


if __name__ == "__main__":
    main()
