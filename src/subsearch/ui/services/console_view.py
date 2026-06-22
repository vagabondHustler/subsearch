from typing import Optional

from PySide6.QtCore import QObject, Signal

from subsearch.runtime.logging.logger import log


class ConsoleViewSink(QObject):
    # Mirrors the terminal's spinner/banner protocol into the GUI. The terminal
    # sink groups output under a spinning banner (a title while running, a
    # done-title when it closes) and lets plain lines logged mid-banner update a
    # single transient line above the spinner. This sink runs the same state
    # machine and turns it into signals the view renders, so the GUI console
    # shows the same grouped, spinner-driven progress rather than a flat dump.
    #
    # Signals fire on the worker thread that drives the run, so consumers must
    # connect with queued connections.
    line_appended = Signal(str)
    banner_started = Signal(str)
    banner_finished = Signal(str)
    status_updated = Signal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._history: list[tuple[str, str]] = []
        self._banner_active = False
        self._pending_done_title = ""
        log.add_sink(self._on_message)

    def _on_message(
        self,
        message: str,
        *,
        is_banner: bool = False,
        title: str | None = None,
        done_title: str | None = None,
        is_last: bool = False,
    ) -> None:
        if is_last:
            self._finish_banner(done_title)
            return
        if is_banner:
            self._finish_banner(None)
            self._start_banner(title or message, done_title or title or message)
            return
        if self._banner_active:
            self._emit("status", message)
        else:
            self._emit("line", message)

    def _start_banner(self, title: str, done_title: str) -> None:
        self._banner_active = True
        self._pending_done_title = done_title
        self._emit("banner", title)

    def _finish_banner(self, done_title: Optional[str]) -> None:
        if not self._banner_active:
            return
        self._banner_active = False
        self._emit("finish", done_title or self._pending_done_title)

    def _emit(self, kind: str, payload: str) -> None:
        self._history.append((kind, payload))
        {
            "line": self.line_appended,
            "banner": self.banner_started,
            "finish": self.banner_finished,
            "status": self.status_updated,
        }[kind].emit(payload)

    def history(self) -> list[tuple[str, str]]:
        return list(self._history)

    def detach(self) -> None:
        log.remove_sink(self._on_message)
