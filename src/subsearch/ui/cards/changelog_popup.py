from PySide6.QtWidgets import QWidget
from qfluentwidgets import TransparentToolButton

from subsearch.ui.icons.lucide import LucideIcon, lucide_qicon
from subsearch.ui.theme.typography import DISABLED_TEXT_COLOR, TEXT_COLOR
from subsearch.ui.widgets.text_popup import MarkdownPopup

EMPTY_CHANGELOG_MESSAGE = "Check for updates to load the changelog."


class ChangelogButton(TransparentToolButton):
    def __init__(self, parent: QWidget) -> None:  # pyright: ignore[reportIncompatibleVariableOverride]
        super().__init__(parent)
        self._popup = MarkdownPopup(self)
        self._has_changelog = False
        self.set_changelog("")
        self.clicked.connect(self._popup.show_above)

    def set_changelog(self, changelog: str) -> None:
        self._popup.set_markdown(changelog or EMPTY_CHANGELOG_MESSAGE)
        self._has_changelog = bool(changelog)
        self._apply_icon_color()

    def _apply_icon_color(self) -> None:
        color = TEXT_COLOR if self._has_changelog else DISABLED_TEXT_COLOR
        self.setIcon(lucide_qicon(LucideIcon.LIST, color))
