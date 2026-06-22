from subsearch.runtime.logging.spinner_console import SpinnerConsole

# A representative run: a banner with two transient lines, a plain line before
# any banner, a second banner, and a final is_last close. The terminal and GUI
# consoles must end up showing the same visible lines.
RECORDS = [
    {"message": "early line"},
    {"message": "--- [Searching] ---", "is_banner": True, "title": "Searching", "done_title": "Searched"},
    {"message": "opensubtitles: searching"},
    {"message": "opensubtitles: found 3"},
    {"message": "--- [Cleaning up] ---", "is_banner": True, "title": "Cleaning up", "done_title": "Cleaned up"},
    {"message": "", "is_last": True},
]


def terminal_visible_lines() -> list[str]:
    printed: list[str] = []
    transient: list[str] = []

    class StubTransient:
        def update(self, spinner, message: str) -> None:
            if transient:
                transient[-1] = message
            else:
                transient.append(message)

        def clear(self, spinner) -> None:
            transient.clear()

    class StubSpinner:
        def __init__(self, text: str) -> None:
            self.text = text

        def start(self) -> None:
            pass

        def stop(self) -> None:
            pass

    console = SpinnerConsole(
        spinner_factory=StubSpinner,
        printer=printed.append,
        transient_line=StubTransient(),
    )
    for record in RECORDS:
        console.write(record["message"], **{key: value for key, value in record.items() if key != "message"})
    return printed


def gui_visible_lines(qtbot) -> list[str]:
    from subsearch.runtime.logging.logger import log
    from subsearch.ui.services.console_view import ConsoleViewSink
    from subsearch.ui.widgets.console_view import ConsoleView

    # The logger is a process-wide singleton; other tests leave records in its
    # history that the sink would replay into the view. Isolate to this sequence.
    log._console_history.clear()
    sink = ConsoleViewSink()
    view = ConsoleView(sink)
    qtbot.addWidget(view)
    dispatch = {
        "line": view._append,
        "banner": view._start_banner,
        "finish": view._finish_banner,
        "status": view._update_status,
    }
    try:
        for record in RECORDS:
            sink._on_message(
                record["message"],
                **{key: value for key, value in record.items() if key != "message"},
            )
        # Drive the view directly from the sink's recorded protocol; the live
        # widget uses queued connections that need an event loop to deliver.
        for kind, payload in sink.history():
            dispatch[kind](payload)
        return [view._list.item(row).text() for row in range(view._list.count())]
    finally:
        sink.detach()


def test_terminal_and_gui_show_the_same_lines(qtbot) -> None:
    # No normalization: the GUI must render finished banners as the plain
    # done-title the terminal prints, with no checkmark or other decoration.
    terminal = terminal_visible_lines()
    gui = gui_visible_lines(qtbot)
    assert terminal == gui
