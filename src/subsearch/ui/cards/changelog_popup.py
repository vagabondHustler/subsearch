from PySide6.QtWidgets import QWidget

from subsearch.ui.icons.lucide import LucideIcon
from subsearch.ui.widgets.icon_caption_button import (
    MutableCaptionToolButton,
    MutableCaptionToolButtonStyle,
)
from subsearch.ui.widgets.text_popup import MarkdownPopup

EMPTY_CHANGELOG_MESSAGE = "Check for updates to load the changelog."


class ChangelogButton(MutableCaptionToolButton):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(MutableCaptionToolButtonStyle(LucideIcon.LOGS, "Changelog"), parent=parent)
        self._popup = MarkdownPopup(self)
        self.set_changelog("")
        self.clicked.connect(self._popup.show_above)

    def set_changelog(self, changelog: str) -> None:
        self._popup.set_markdown(changelog or EMPTY_CHANGELOG_MESSAGE)
        self.setEnabled(bool(changelog))
