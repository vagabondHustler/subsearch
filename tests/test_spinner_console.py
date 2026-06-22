import logging

from subsearch.runtime.logging.events import LogEvent
from subsearch.runtime.logging.logger import Logger
from subsearch.runtime.logging.spinner_console import (
    SpinnerConsole,
    SpinnerStyle,
)


def make_logger(monkeypatch):
    monkeypatch.setattr(Logger, "_build_terminal_sink", staticmethod(lambda: None))
    instance = Logger()
    monkeypatch.setattr(type(instance), "file_logger", property(lambda self: logging.getLogger("test_subsearch")))
    calls: list[dict] = []
    instance._sinks = [
        lambda message, *, is_banner=False, title=None, done_title=None, is_last=False: calls.append(
            {
                "message": message,
                "is_banner": is_banner,
                "title": title,
                "done_title": done_title,
                "is_last": is_last,
            }
        )
    ]
    return instance, calls


def test_event_marks_banner_with_title(monkeypatch):
    instance, calls = make_logger(monkeypatch)
    instance.event(LogEvent.SPINNER, title="Initializing")
    assert calls[-1]["is_banner"] is True
    assert calls[-1]["title"] == "Initializing"


def test_event_non_banner_clears_flag(monkeypatch):
    instance, calls = make_logger(monkeypatch)
    instance.event(LogEvent.SEARCH_COMPLETED)
    assert calls[-1]["is_banner"] is False
    assert calls[-1]["title"] is None


def test_info_is_not_banner(monkeypatch):
    instance, calls = make_logger(monkeypatch)
    instance.info("plain line")
    assert calls[-1]["is_banner"] is False


class FakeSpinner:
    def __init__(self, text: str) -> None:
        self.text = text
        self.started = False
        self.stopped = False

    def start(self) -> None:
        self.started = True

    def stop(self) -> None:
        self.stopped = True

    def hide(self) -> None:
        pass

    def show(self) -> None:
        pass


class FakeTransientLine:
    def __init__(self) -> None:
        self.events: list[tuple[str, str]] = []

    def update(self, spinner, message: str) -> None:
        self.events.append(("update", message))

    def clear(self, spinner) -> None:
        self.events.append(("clear", ""))


def build():
    spinners: list[FakeSpinner] = []
    laps: list[str] = []
    transient = FakeTransientLine()

    def factory(text: str) -> FakeSpinner:
        spinner = FakeSpinner(text)
        spinners.append(spinner)
        return spinner

    console = SpinnerConsole(
        spinner_factory=factory,
        printer=laps.append,
        transient_line=transient,
    )
    console._test_transient = transient
    return console, spinners, laps


def test_banner_starts_spinner_with_title():
    console, spinners, laps = build()
    console.write("--- [Initializing] ---", is_banner=True, title="Initializing")
    assert len(spinners) == 1
    assert spinners[0].text == "Initializing"
    assert spinners[0].started is True
    assert laps == []


def test_non_banner_line_updates_transient_line_above_spinner():
    console, spinners, laps = build()
    console.write("--- [Initializing] ---", is_banner=True, title="Initializing")
    console.write("Verifying files and paths")
    console.write("Initializing system tray icon")
    assert spinners[0].text == "Initializing"
    assert console._test_transient.events == [
        ("update", "Verifying files and paths"),
        ("update", "Initializing system tray icon"),
    ]
    assert laps == []


def test_transient_line_is_cleared_when_spinner_finishes():
    console, _, laps = build()
    console.write("--- [Initializing] ---", is_banner=True, title="Initializing")
    console.write("Verifying files and paths")
    console.close()
    assert console._test_transient.events == [("update", "Verifying files and paths"), ("clear", "")]
    assert laps == ["Initializing"]


def test_next_banner_prints_title_and_opens_new():
    console, spinners, laps = build()
    console.write("--- [Initializing] ---", is_banner=True, title="Initializing")
    console.write("--- [AppConfig] ---", is_banner=True, title="AppConfig")
    assert laps == ["Initializing"]
    assert spinners[0].stopped is True
    assert spinners[1].text == "AppConfig"


def test_finished_banner_prints_done_title_when_given():
    console, spinners, laps = build()
    console.write("--- [Searching] ---", is_banner=True, title="Searching", done_title="Searched")
    console.close()
    assert spinners[0].text == "Searching"
    assert laps == ["Searched"]


def test_finished_banner_falls_back_to_title_without_done_title():
    console, _, laps = build()
    console.write("--- [Searching] ---", is_banner=True, title="Searching")
    console.close()
    assert laps == ["Searching"]


def test_close_is_idempotent_and_prints_final_title_once():
    console, _, laps = build()
    console.write("--- [Searching] ---", is_banner=True, title="Searching")
    console.close()
    console.close()
    assert laps == ["Searching"]


def test_is_last_prints_title_and_opens_no_new_spinner():
    console, spinners, laps = build()
    console.write("--- [Cleaning up] ---", is_banner=True, title="Cleaning up")
    console.write("", is_last=True)
    assert laps == ["Cleaning up"]
    assert spinners[0].stopped is True
    assert len(spinners) == 1


def test_is_last_without_active_spinner_is_noop():
    console, spinners, laps = build()
    console.write("", is_last=True)
    assert spinners == []
    assert laps == []


def test_line_before_first_banner_is_printed():
    console, _, laps = build()
    console.write("early line")
    assert laps == ["early line"]


def test_default_factory_forwards_no_style_when_unset(monkeypatch):
    captured: dict = {}

    def fake_yaspin(**kwargs):
        captured.update(kwargs)
        return FakeSpinner(kwargs.get("text", ""))

    monkeypatch.setattr("yaspin.yaspin", fake_yaspin)
    console = SpinnerConsole()
    console.write("--- [X] ---", is_banner=True, title="X")
    assert set(captured) == {"text", "spinner"}


def test_default_factory_forwards_set_style_fields(monkeypatch):
    captured: dict = {}

    def fake_yaspin(**kwargs):
        captured.update(kwargs)
        return FakeSpinner(kwargs.get("text", ""))

    monkeypatch.setattr("yaspin.yaspin", fake_yaspin)
    console = SpinnerConsole(style=SpinnerStyle(color="cyan", attrs=["bold"]))
    console.write("--- [X] ---", is_banner=True, title="X")
    assert captured["color"] == "cyan"
    assert captured["attrs"] == ["bold"]
    assert "on_color" not in captured
    assert "spinner" in captured


class RecordingSpinner:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def hide(self) -> None:
        self.calls.append("hide")

    def show(self) -> None:
        self.calls.append("show")


class FakeStream:
    def __init__(self) -> None:
        self.writes: list[str] = []

    def write(self, text: str) -> None:
        self.writes.append(text)

    def flush(self) -> None:
        pass


def test_transient_line_first_update_creates_line_below_hidden_spinner():
    from subsearch.runtime.logging.spinner_console import TransientLine

    spinner = RecordingSpinner()
    stream = FakeStream()
    line = TransientLine(stream=stream)
    line.update(spinner, "Verifying files and paths")
    assert spinner.calls == ["hide", "show"]
    assert stream.writes == ["Verifying files and paths\n"]


def test_transient_line_second_update_rewrites_line_in_place():
    from subsearch.runtime.logging.spinner_console import TransientLine

    spinner = RecordingSpinner()
    stream = FakeStream()
    line = TransientLine(stream=stream)
    line.update(spinner, "first")
    line.update(spinner, "second")
    assert stream.writes[-1] == "\033[A\r\033[Ksecond\n"


def test_transient_line_clear_is_noop_until_shown():
    from subsearch.runtime.logging.spinner_console import TransientLine

    spinner = RecordingSpinner()
    stream = FakeStream()
    line = TransientLine(stream=stream)
    line.clear(spinner)
    assert stream.writes == []
    assert spinner.calls == []
    line.update(spinner, "x")
    line.clear(spinner)
    assert stream.writes[-1] == "\033[A\r\033[K"
