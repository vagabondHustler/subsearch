from PySide6.QtWidgets import QWidget

from subsearch.runtime.config.defaults import ConfigKey
from subsearch.ui.icons.lucide import LucideIcon
from subsearch.ui.state.store import SettingsStore
from subsearch.ui.theme import palette
from subsearch.ui.theme.metrics import POST_PROCESSING_ICON_SIZE
from subsearch.ui.theme.typography import POST_PROCESSING_FONT_SIZE
from subsearch.ui.widgets.icon_caption_button import (
    CaptionedToolToggle,
    CaptionToolToggleStyle,
)


class PostProcessingToggle(CaptionedToolToggle):

    def __init__(
        self,
        store: SettingsStore,
        parent: QWidget | None = None,
        icon_size: int = POST_PROCESSING_ICON_SIZE,
        caption_font_size: int = POST_PROCESSING_FONT_SIZE,
    ) -> None:
        super().__init__(
            CaptionToolToggleStyle(
                icon=LucideIcon.COLUMNS_3_COG_SPECIAL,
                checked_caption="MANUAL",
                unchecked_caption="AUTO",
                checked_color=palette.ORANGE,
                icon_size=icon_size,
                caption_font_size=caption_font_size,
            ),
            parent=parent,
        )
        self._store = store
        self.render_state(bool(store.read(ConfigKey.SUBTITLE_WORKSPACE_MANUAL_POST_PROCESSING)))
        self.toggled.connect(self._on_toggled)
        store.subscribe(ConfigKey.SUBTITLE_WORKSPACE_MANUAL_POST_PROCESSING, self.render_state)

    def _on_toggled(self, manual_enabled: bool) -> None:
        self._store.write(ConfigKey.SUBTITLE_WORKSPACE_MANUAL_POST_PROCESSING, manual_enabled)
