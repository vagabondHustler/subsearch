import atexit
import sys
import threading
from dataclasses import asdict, dataclass
from typing import Any, Callable, Optional

SpinnerFactory = Callable[[str], Any]
Printer = Callable[[str], None]


class TransientLine:
    # A single line that lives directly above a running yaspin spinner and updates
    # in place. yaspin's hide()/show() are the only race-safe way to touch the
    # terminal while it animates: hide() takes yaspin's stream lock, pauses the
    # spin thread, and clears its line; show() resumes. Between them the spin
    # thread is parked, so writing to the same stdout is safe.
    def __init__(self, stream: Any = None) -> None:
        self._stream = stream or sys.stdout
        self._visible = False

    def update(self, spinner: Any, message: str) -> None:
        spinner.hide()
        if self._visible:
            # cursor up to the existing line, return to col 0, clear it, rewrite,
            # then newline back down to the (now cleared) spinner line.
            self._stream.write(f"\033[A\r\033[K{message}\n")
        else:
            self._stream.write(f"{message}\n")
            self._visible = True
        self._stream.flush()
        spinner.show()

    def clear(self, spinner: Any) -> None:
        if not self._visible:
            return
        spinner.hide()
        # cursor up to the line, return to col 0, clear it; spinner's own line is
        # already cleared by hide(), so the spinner redraws one line higher.
        self._stream.write("\033[A\r\033[K")
        self._stream.flush()
        self._visible = False
        spinner.show()


@dataclass(frozen=True)
class SpinnerStyle:
    # Optional yaspin styling (termcolor values). Every field defaults to None so nothing is
    # forced and yaspin's own defaults apply; only the set fields are forwarded to yaspin(...).
    spinner: Optional[object] = None
    color: Optional[str] = None
    on_color: Optional[str] = None
    attrs: Optional[list[str]] = None


class SpinnerConsole:
    def __init__(
        self,
        *,
        spinner_factory: Optional[SpinnerFactory] = None,
        style: SpinnerStyle = SpinnerStyle(),
        printer: Printer = print,
        transient_line: Optional[Any] = None,
    ) -> None:
        self._spinner_factory = spinner_factory or self._build_styled_factory(style)
        self._printer = printer
        self._transient_line = transient_line or TransientLine()
        self._lock = threading.Lock()
        self._spinner: Optional[Any] = None
        self._title: Optional[str] = None
        self._done_title: Optional[str] = None
        atexit.register(self.close)

    @staticmethod
    def _build_styled_factory(style: SpinnerStyle) -> SpinnerFactory:
        kwargs = {key: value for key, value in asdict(style).items() if value is not None}

        def factory(text: str) -> Any:
            from yaspin import yaspin
            from yaspin.spinners import Spinners

            kwargs.setdefault("spinner", Spinners.arc)
            return yaspin(text=text, **kwargs)

        return factory

    def write(
        self,
        message: str,
        *,
        is_banner: bool = False,
        title: Optional[str] = None,
        done_title: Optional[str] = None,
        is_last: bool = False,
    ) -> None:
        with self._lock:
            if is_last:
                self._finish_current()
                return
            if is_banner:
                self._finish_current()
                self._start(title or message, done_title)
                return
            if self._spinner is None:
                self._printer(message)
            else:
                self._transient_line.update(self._spinner, message)

    def close(self) -> None:
        with self._lock:
            self._finish_current()

    def __enter__(self) -> "SpinnerConsole":
        return self

    def __exit__(self, *exception: object) -> None:
        self.close()

    def _start(self, title: str, done_title: Optional[str] = None) -> None:
        self._title = title
        self._done_title = done_title or title
        self._spinner = self._spinner_factory(title)
        self._spinner.start()

    def _finish_current(self) -> None:
        if self._spinner is None:
            return
        self._transient_line.clear(self._spinner)
        self._spinner.stop()
        assert self._done_title is not None
        self._printer(self._done_title)
        self._spinner = None
        self._title = None
        self._done_title = None
