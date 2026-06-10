from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QWidget

SEPARATOR_DARK = "32, 32, 32"
SEPARATOR_LIGHT = "52, 53, 55"
SEPARATOR_INSET = 24


def _fading_line(rgb: str, opacity: float) -> QFrame:
    line = QFrame()
    line.setFixedHeight(1)
    alpha = round(255 * opacity)
    solid = f"rgba({rgb}, {alpha})"
    clear = f"rgba({rgb}, 0)"
    gradient = (
        f"qlineargradient(x1:0, y1:0, x2:1, y2:0, "
        f"stop:0 {clear}, stop:0.15 {solid}, stop:0.85 {solid}, stop:1 {clear})"
    )
    line.setStyleSheet(f"background-color: {gradient};")
    return line


def _stacked_lines(opacity: float) -> QWidget:
    stack = QWidget()
    layout = QVBoxLayout(stack)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)
    layout.addWidget(_fading_line(SEPARATOR_DARK, opacity))
    layout.addWidget(_fading_line(SEPARATOR_LIGHT, opacity))
    return stack


def make_fading_separator(opacity: float = 1.0, width_fraction: float = 1.0) -> QWidget:
    container = QWidget()
    container.setFixedHeight(2)
    layout = QHBoxLayout(container)
    layout.setContentsMargins(SEPARATOR_INSET, 0, SEPARATOR_INSET, 0)
    layout.setSpacing(0)
    side = round((1 - width_fraction) * 100 / 2)
    layout.addStretch(side)
    layout.addWidget(_stacked_lines(opacity), stretch=round(width_fraction * 100))
    layout.addStretch(side)
    return container
