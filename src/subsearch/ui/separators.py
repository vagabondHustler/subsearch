from PySide6.QtWidgets import QFrame, QVBoxLayout, QWidget

SEPARATOR_DARK = "44, 44, 44"
SEPARATOR_LIGHT = "70, 70, 70"
SEPARATOR_INSET = 24


def _fading_line(rgb: str) -> QFrame:
    line = QFrame()
    line.setFixedHeight(1)
    solid = f"rgba({rgb}, 255)"
    clear = f"rgba({rgb}, 0)"
    gradient = (
        f"qlineargradient(x1:0, y1:0, x2:1, y2:0, "
        f"stop:0 {clear}, stop:0.15 {solid}, stop:0.85 {solid}, stop:1 {clear})"
    )
    line.setStyleSheet(f"background-color: {gradient};")
    return line


def make_fading_separator() -> QWidget:
    container = QWidget()
    container.setFixedHeight(2)
    layout = QVBoxLayout(container)
    layout.setContentsMargins(SEPARATOR_INSET, 0, SEPARATOR_INSET, 0)
    layout.setSpacing(0)
    layout.addWidget(_fading_line(SEPARATOR_DARK))
    layout.addWidget(_fading_line(SEPARATOR_LIGHT))
    return container
