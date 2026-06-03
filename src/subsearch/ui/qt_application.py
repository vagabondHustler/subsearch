import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

APPLICATION_FONT_FAMILY = "Segoe UI"
APPLICATION_FONT_PIXEL_SIZE = 12


def get_application() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing

    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    application = QApplication(sys.argv)
    application_font = QFont(APPLICATION_FONT_FAMILY)
    application_font.setPixelSize(APPLICATION_FONT_PIXEL_SIZE)
    application_font.setWeight(QFont.Weight.DemiBold)
    application.setFont(application_font)
    return application
