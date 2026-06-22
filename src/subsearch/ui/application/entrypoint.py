import sys
from typing import Callable

from PySide6.QtCore import QMessageLogContext, QtMsgType, qInstallMessageHandler
from qfluentwidgets import Theme, setTheme, setThemeColor

from subsearch.runtime.logging.events import LogEvent
from subsearch.runtime.logging.logger import log
from subsearch.runtime.models import Subtitle
from subsearch.ui import warmup
from subsearch.ui.application.window import SettingsWindow
from subsearch.ui.compat.qfluent import ACCENT_COLOR, force_fixed_accent_color
from subsearch.ui.qt_application import get_application
from subsearch.ui.services.search import SearchJobProtocol
from subsearch.ui.theme.typography import TEXT_COLOR


def _suppress_point_size_warning(message_type: QtMsgType, context: QMessageLogContext, message: str) -> None:
    if "setPointSize" in message:
        return
    sys.stderr.write(f"{message}\n")


def open_settings_window(
    subtitles: list[Subtitle] | None = None,
    search_job_factory: Callable[..., SearchJobProtocol] | None = None,
    start_search_immediately: bool = False,
    on_window_shown: Callable[[], None] | None = None,
) -> list[Subtitle]:
    warmup.await_warmup()
    qInstallMessageHandler(_suppress_point_size_warning)
    application = get_application()
    setTheme(Theme.DARK)
    setThemeColor(ACCENT_COLOR)
    force_fixed_accent_color()
    application.setStyleSheet(
        f"QLabel, CheckBox, RadioButton, BodyLabel, CaptionLabel, SubtitleLabel, "
        f"TitleLabel, StrongBodyLabel, SpinBox, ComboBox, LineEdit, "
        f"#headerLabel, #titleLabel {{ color: {TEXT_COLOR}; }}"
        f"HeaderCardWidget, CardWidget, SimpleCardWidget, ElevatedCardWidget "
        f"{{ background-color: transparent; border: none; }}"
    )
    window = SettingsWindow(subtitles, search_job_factory, start_search_immediately=start_search_immediately)
    log.event(LogEvent.BOOT_UI_OPENED)
    if not start_search_immediately:
        # When a search runs immediately the search worker owns the banner sequence
        # ("Searching" -> "Searched" -> "Waiting for user inputs"); starting one here
        # would be torn down by it and emit a spurious "Processed user inputs".
        log.event(LogEvent.SPINNER, title="Waiting for user inputs", done_title="Processed user inputs")
    window.show()
    if on_window_shown is not None:
        on_window_shown()
    application.exec()
    log.event(LogEvent.BOOT_UI_CLOSED, level="debug")
    log.end_banner()
    return window.manual_search_interface.downloaded
