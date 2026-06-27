import winsound
from pathlib import Path

from PySide6.QtCore import (
    Property,
    QEasingCurve,
    QPoint,
    QPropertyAnimation,
    QSequentialAnimationGroup,
    Qt,
    Signal,
)
from PySide6.QtGui import (
    QColor,
    QGuiApplication,
    QMouseEvent,
    QPainter,
    QPainterPath,
    QPaintEvent,
    QShowEvent,
)
from PySide6.QtWidgets import (
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from subsearch.ui.compat.qfluent import apply_popup_acrylic
from subsearch.ui.icons.lucide import LucideIcon, lucide_qicon
from subsearch.ui.theme import metrics, palette, typography
from subsearch.ui.theme.separators import make_fading_separator

# Tint painted over the blurred backdrop; POPUP_BACKGROUND at ~70% opacity.
TOAST_ACRYLIC_ALPHA = 179

# The same chime the native Windows toast plays; shipped with every Windows install.
NOTIFICATION_SOUND_FILE = Path(r"C:\Windows\Media\Windows Notify System Generic.wav")

FADE_IN_DURATION_MS = 220
HOLD_DURATION_MS = 1200
FADE_OUT_DURATION_MS = 360


class NotificationToast(QWidget):
    dismissed = Signal()

    def __init__(
        self,
        title: str,
        summary: str,
        succeeded: bool,
        hold_duration_ms: int = HOLD_DURATION_MS,
        play_sound: bool = False,
    ) -> None:
        super().__init__(None)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setFixedWidth(metrics.TOAST_WIDTH)

        self._status_color = palette.GREEN if succeeded else palette.RED
        self._hold_duration_ms = max(0, hold_duration_ms)
        self._is_dismissed = False
        self._acrylic = True
        self._play_sound = play_sound
        self._build_layout(title, summary)
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self._opacity_effect.setOpacity(0.0)
        self.setGraphicsEffect(self._opacity_effect)
        self._animation = self._build_animation()

    def _build_layout(self, title: str, summary: str) -> None:
        outer = QVBoxLayout(self)
        inset = metrics.TOAST_PADDING
        outer.setContentsMargins(inset, inset, inset, inset)
        outer.setSpacing(metrics.TOAST_CONTENT_GAP)

        outer.addLayout(self._build_header(title))
        outer.addWidget(make_fading_separator(opacity=0.55, width_fraction=0.9, inset=0))

        message = QLabel(summary, self)
        message.setWordWrap(True)
        typography.apply_caption_font(message)
        outer.addWidget(message)

    def _build_header(self, title: str) -> QHBoxLayout:
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(metrics.TOAST_CONTENT_GAP)

        status_icon = QLabel(self)
        status_icon.setPixmap(
            lucide_qicon(LucideIcon.CIRCLE_SMALL, self._status_color).pixmap(
                metrics.TOAST_ICON_SIZE, metrics.TOAST_ICON_SIZE
            )
        )
        header.addWidget(status_icon)

        name = QLabel(title, self)
        typography.apply_body_font(name)
        header.addWidget(name)
        header.addStretch(1)

        header.addWidget(self._build_close_button())
        return header

    def _build_close_button(self) -> QToolButton:
        close_button = QToolButton(self)
        close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        close_button.setIcon(lucide_qicon(LucideIcon.X, typography.MUTED_TEXT_COLOR))
        close_button.setFixedSize(metrics.TOAST_CLOSE_BUTTON_SIZE, metrics.TOAST_CLOSE_BUTTON_SIZE)
        close_button.setStyleSheet("QToolButton { border: none; background: transparent; }")
        close_button.clicked.connect(self.dismiss)
        return close_button

    def _play_notification_sound(self) -> None:
        if not NOTIFICATION_SOUND_FILE.exists():
            return
        try:
            winsound.PlaySound(
                str(NOTIFICATION_SOUND_FILE),
                winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT,
            )
        except RuntimeError:
            return

    def _build_animation(self) -> QSequentialAnimationGroup:
        fade_in = QPropertyAnimation(self, b"window_opacity")
        fade_in.setDuration(FADE_IN_DURATION_MS)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)

        fade_out = QPropertyAnimation(self, b"window_opacity")
        fade_out.setDuration(FADE_OUT_DURATION_MS)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        fade_out.setEasingCurve(QEasingCurve.Type.InCubic)

        sequence = QSequentialAnimationGroup(self)
        sequence.addAnimation(fade_in)
        sequence.addPause(self._hold_duration_ms)
        sequence.addAnimation(fade_out)
        sequence.finished.connect(self.dismiss)
        return sequence

    def _window_opacity(self) -> float:
        return self._opacity_effect.opacity()

    def _set_window_opacity(self, opacity: float) -> None:
        self._opacity_effect.setOpacity(opacity)

    window_opacity = Property(float, _window_opacity, _set_window_opacity)

    def showEvent(self, event: QShowEvent) -> None:
        # Reapplied on every show: hiding can recreate the native window, and the
        # compositor effect is bound to the old window handle.
        if self._acrylic and not apply_popup_acrylic(self):
            self._acrylic = False
        super().showEvent(event)

    def show_above_clock(self) -> None:
        self._move_above_clock()
        self.show()
        if self._play_sound:
            self._play_notification_sound()
        self._animation.start()

    def _move_above_clock(self) -> None:
        screen = QGuiApplication.primaryScreen()
        available = screen.availableGeometry()
        self.adjustSize()
        x = available.right() - self.width() - metrics.TOAST_SCREEN_INSET
        y = available.bottom() - self.height() - metrics.TOAST_SCREEN_INSET
        self.move(QPoint(x, y))

    def dismiss(self) -> None:
        if self._is_dismissed:
            return
        self._is_dismissed = True
        if self._animation.state() == QSequentialAnimationGroup.State.Running:
            self._animation.stop()
        self.close()
        self.dismissed.emit()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.dismiss()
            return
        super().mousePressEvent(event)

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        radius = metrics.TOAST_CORNER_RADIUS
        rect = self.rect().adjusted(0, 0, -1, -1)

        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)
        painter.fillPath(path, self._background_color())

        painter.setPen(QColor(palette.POPUP_BORDER))
        painter.drawPath(path)

    def _background_color(self) -> QColor:
        background = QColor(palette.POPUP_BACKGROUND)
        if self._acrylic:
            background.setAlpha(TOAST_ACRYLIC_ALPHA)
        return background
