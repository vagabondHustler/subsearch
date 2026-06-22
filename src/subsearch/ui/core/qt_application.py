import signal
import sys

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

APPLICATION_FONT_FAMILY = "Segoe UI"
APPLICATION_FONT_PIXEL_SIZE = 12
SIGINT_POLL_INTERVAL_MS = 200


def get_application() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing

    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    application = QApplication(sys.argv)
    application_font = QFont(APPLICATION_FONT_FAMILY)
    application_font.setPixelSize(APPLICATION_FONT_PIXEL_SIZE)
    application_font.setWeight(QFont.Weight.DemiBold)
    application.setFont(application_font)
    _enable_keyboard_interrupt(application)
    return application


def _enable_keyboard_interrupt(application: QApplication) -> None:
    signal.signal(signal.SIGINT, lambda *_: application.quit())
    # Qt's C++ event loop never yields to the Python interpreter on its own, so the
    # installed SIGINT handler can only run while Python has control. A periodic no-op
    # timer hands control back often enough for Ctrl+C to be honored.
    sigint_timer = QTimer(application)
    sigint_timer.timeout.connect(lambda: None)
    sigint_timer.start(SIGINT_POLL_INTERVAL_MS)
