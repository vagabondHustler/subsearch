import sys
from typing import Callable

from PySide6.QtCore import QMessageLogContext, QtMsgType, qInstallMessageHandler
from PySide6.QtWidgets import QApplication
from qfluentwidgets import Theme, setTheme, setThemeColor

from subsearch.runtime.models import Subtitle, WorkspaceOutcome
from subsearch.runtime.recorder import LogLevel, capture, phase
from subsearch.ui import warmup
from subsearch.ui.compat.qfluent import ACCENT_COLOR, force_fixed_accent_color
from subsearch.ui.core.qt_application import get_application
from subsearch.ui.core.window import SettingsWindow
from subsearch.ui.services.search import SearchJobProtocol
from subsearch.ui.theme.typography import TEXT_COLOR


def _suppress_point_size_warning(message_type: QtMsgType, context: QMessageLogContext, message: str) -> None:
    if "setPointSize" in message:
        return
    sys.stderr.write(f"{message}\n")


def _build_application() -> QApplication:
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
    return application


def _start_waiting_banner_unless_search_owns_it(start_search_immediately: bool) -> None:
    if start_search_immediately:
        # The search worker owns the banner sequence ("Searching" -> "Idle");
        # starting one here would be torn down by it.
        return
    phase("Idle")


def open_settings_window(
    subtitles: list[Subtitle] | None = None,
    search_job_factory: Callable[..., SearchJobProtocol] | None = None,
    start_search_immediately: bool = False,
    on_window_shown: Callable[[], None] = lambda: None,
) -> WorkspaceOutcome:
    application = _build_application()
    window = SettingsWindow(subtitles, search_job_factory, start_search_immediately=start_search_immediately)
    capture("UI opened")
    _start_waiting_banner_unless_search_owns_it(start_search_immediately)
    window.show()
    on_window_shown()
    application.exec()
    capture("UI closed", level=LogLevel.DEBUG)
    interface = window.manual_search_interface
    return WorkspaceOutcome(interface.downloaded, interface.placed_best_next_to_video)
