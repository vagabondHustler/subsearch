from PySide6.QtCore import QEvent, QObject, QRegularExpression, QSize, Qt, Signal
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import QVBoxLayout, QWidget
from qfluentwidgets import CaptionLabel, LineEdit

from subsearch.ui.compat.qfluent import (
    HANDLE_CENTER,
    HANDLE_SIZE,
    CircleDotSlider,
    make_line_edit_chromeless,
)
from subsearch.ui.theme.typography import apply_body_font, apply_caption_font

TRACK_ALIGNED_LABEL_WIDTH = 150
EDIT_TEXT_PADDING = 24


class SliderWithValueLabel(QWidget):
    valueChanged = Signal(int)
    sliderReleased = Signal()

    def __init__(self, suffix: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._suffix = suffix
        self._slider = CircleDotSlider(Qt.Orientation.Horizontal, self)
        self._edit = LineEdit(self)
        apply_body_font(self._edit)
        make_line_edit_chromeless(self._edit)
        self._edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._edit.setClearButtonEnabled(False)
        # digits only; the suffix is purely cosmetic and removed while editing
        self._edit.setValidator(QRegularExpressionValidator(QRegularExpression(r"^\d{1,3}$"), self))
        self._edit.installEventFilter(self)
        self._edit.editingFinished.connect(self._on_edit_finished)
        self._slider.valueChanged.connect(self._on_value_changed)
        self._slider.sliderReleased.connect(self.sliderReleased)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched is self._edit and event.type() == QEvent.Type.FocusIn:
            self._show_bare_value_for_editing()
        return False

    def _show_bare_value_for_editing(self) -> None:
        self._edit.setText(str(self._slider.value()))
        self._edit.setFixedWidth(self._edit_width_for_text(str(self._slider.maximum())))
        self._update_edit_pos()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        edit_h = self._edit.sizeHint().height()
        inset = self._track_side_inset()
        self._slider.setGeometry(inset, edit_h + 4, self.width() - 2 * inset, HANDLE_SIZE)
        self._update_edit_pos()

    def _track_side_inset(self) -> int:
        widest_text = self._format_value(self._slider.maximum())
        return max(0, self._edit_width_for_text(widest_text) // 2 - HANDLE_CENTER)

    def _edit_width_for_text(self, text: str) -> int:
        return self._edit.fontMetrics().horizontalAdvance(text) + EDIT_TEXT_PADDING

    def _fit_edit_to_text(self) -> None:
        self._edit.setFixedWidth(self._edit_width_for_text(self._edit.text()))

    def sizeHint(self) -> QSize:
        edit_h = self._edit.sizeHint().height()
        return QSize(200, edit_h + 4 + HANDLE_SIZE)

    def minimumSizeHint(self) -> QSize:
        return self.sizeHint()

    def _update_edit_pos(self) -> None:
        if self._slider.width() == 0:
            return
        value = self._slider.value()
        minimum, maximum = self._slider.minimum(), self._slider.maximum()
        t = (value - minimum) / (maximum - minimum) if maximum > minimum else 0
        handle_center_x = self._slider.x() + HANDLE_CENTER + round(t * (self._slider.width() - HANDLE_SIZE))
        self._edit.move(handle_center_x - self._edit.width() // 2 + self._suffix_center_shift(), 0)

    def _suffix_center_shift(self) -> int:
        if not self._suffix or self._edit.hasFocus():
            return 0
        return self._edit.fontMetrics().horizontalAdvance(f" {self._suffix}") // 2

    def _format_value(self, value: int) -> str:
        return f"{value} {self._suffix}" if self._suffix else str(value)

    def _set_edit_text(self, value: int) -> None:
        self._edit.setText(self._format_value(value))
        self._fit_edit_to_text()

    def _on_edit_finished(self) -> None:
        minimum, maximum = self._slider.minimum(), self._slider.maximum()
        try:
            value = int(self._edit.text().strip())
        except ValueError:
            value = self._slider.value()
        value = max(minimum, min(value, maximum))
        self._set_edit_text(value)
        if value != self._slider.value():
            self._slider.setValue(value)
        self._edit.clearFocus()
        self._update_edit_pos()
        self.sliderReleased.emit()

    def _on_value_changed(self, value: int) -> None:
        self._set_edit_text(value)
        self._update_edit_pos()
        self.valueChanged.emit(value)

    def setValue(self, value: int) -> None:
        self._slider.setValue(value)

    def set_value_silent(self, value: int) -> None:
        self._slider.set_value_silent(value)
        self._set_edit_text(value)
        self._update_edit_pos()

    def value(self) -> int:
        return self._slider.value()

    def setRange(self, minimum: int, maximum: int) -> None:
        self._slider.setRange(minimum, maximum)
        inset = self._track_side_inset()
        self._slider.setGeometry(inset, self.track_top_offset(), self.width() - 2 * inset, HANDLE_SIZE)
        self._update_edit_pos()

    def track_top_offset(self) -> int:
        return self._edit.sizeHint().height() + 4

    def commit_edit(self) -> None:
        self._on_edit_finished()


def track_aligned_label(text: str, slider: SliderWithValueLabel, parent: QWidget) -> QWidget:
    label = CaptionLabel(text, parent)
    apply_caption_font(label)
    label.setFixedWidth(TRACK_ALIGNED_LABEL_WIDTH)

    container = QWidget(parent)
    container.setFixedWidth(TRACK_ALIGNED_LABEL_WIDTH)
    column = QVBoxLayout(container)
    track_center_offset = (HANDLE_SIZE - label.sizeHint().height()) // 2
    column.setContentsMargins(0, slider.track_top_offset() + track_center_offset, 0, 0)
    column.setSpacing(0)
    column.addWidget(label, 0, Qt.AlignmentFlag.AlignTop)
    column.addStretch(1)
    return container
