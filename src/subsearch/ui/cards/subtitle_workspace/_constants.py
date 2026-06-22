from subsearch.ui.cards.subtitle_workspace.splitter import _HANDLE_LINE_WIDTH_FRACTION
from subsearch.ui.icons.lucide import LucideIcon
from subsearch.ui.theme import palette

CARD_BODY_MARGINS = (12, 8, 12, 12)

LIST_FONT_FAMILY = "Segoe UI Semibold"
ICON_SIZE = 16
ROW_HEIGHT = 26

LIST_STYLE_SHEET = """
ListWidget {
    background: transparent;
    border: none;
    outline: none;
}
ListWidget::item {
    background: transparent;
    border: none;
    padding-left: 4px;
}
ListWidget::item:hover,
ListWidget::item:selected {
    background: rgba(255, 255, 255, 18);
    border: none;
    border-radius: 4px;
}
"""

# The two trailing action icons sit tight together as one control group; the
# rightmost one is inset by ROW_INSET so it lines up with the card header's lamp.
ACTION_BUTTON_GAP = 0

PENDING_COLOR = palette.NEUTRAL_1
DOWNLOADING_COLOR = palette.BLUE
SUCCESS_COLOR = palette.GREEN
FAILED_COLOR = palette.RED

PENDING_ICON = LucideIcon.CIRCLE
# Sentinel marking the downloading state; rendered as the ripple animation, not this icon.
DOWNLOADING_ICON = LucideIcon.CIRCLE_DOT_DASHED
SUCCESS_ICON = LucideIcon.CIRCLE_CHECK_BIG
FAILED_ICON = LucideIcon.CIRCLE_X

FILTER_BAR_WIDTH = 200

# Match the splitter handle's centered line (_HANDLE_LINE_WIDTH_FRACTION) so the
# search field and the separator below it span the same width.
SEARCH_BAR_WIDTH_FRACTION = _HANDLE_LINE_WIDTH_FRACTION

IDLE_PLACEHOLDER_TEXT = "Drag and drop a video, or or use the search bar"
SEARCHING_PLACEHOLDER_TEXT = "Searching for subtitles…"
NO_RESULTS_PLACEHOLDER_TEXT = "No subtitles found"
