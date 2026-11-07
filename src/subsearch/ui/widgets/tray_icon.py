from PySide6.QtGui import QCursor, QIcon
from PySide6.QtWidgets import QSystemTrayIcon, QWidget

from subsearch.runtime.config import APP_PATHS
from subsearch.ui.icons.lucide import LucideIcon
from subsearch.ui.services.issue_reporting import open_bug_report
from subsearch.ui.widgets.context_menu_popup import ContextMenuItem, ContextMenuPopup

TOOLTIP = "Subsearch"


class WindowTrayIcon(QSystemTrayIcon):
    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self._window = window
        self._menu: ContextMenuPopup | None = None
        self.setIcon(QIcon(str(APP_PATHS.ui_assets / "subsearch.ico")))
        self.setToolTip(TOOLTIP)
        self.activated.connect(self._on_activated)

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show_window()
        elif reason == QSystemTrayIcon.ActivationReason.Context:
            self._open_menu()

    def _open_menu(self) -> None:
        items = [
            ContextMenuItem(LucideIcon.EYE, "Show Subsearch", self.show_window),
            ContextMenuItem(LucideIcon.BUG, "Report bug", open_bug_report),
            ContextMenuItem(LucideIcon.X, "Exit", self._close_window),
        ]
        self._menu = ContextMenuPopup(self._window, items)
        self._menu.show_above_point(QCursor.pos())

    def show_window(self) -> None:
        self._window.showNormal()
        self._window.raise_()
        self._window.activateWindow()

    def _close_window(self) -> None:
        self._window.close()
