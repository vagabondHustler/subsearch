from typing import Any

from PySide6.QtCore import QSize, Qt, QTimer, Signal
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QVBoxLayout, QWidget
from qfluentwidgets import (
    CaptionLabel,
    CheckBox,
    TransparentToolButton,
)

from subsearch.parsing.release_parser import score_subtitle_tokens
from subsearch.runtime.config import PROVIDER_DISPLAY_NAMES, Provider
from subsearch.runtime.config.defaults import (
    DEFAULT_TOKEN_MULTIPLIERS,
    DEFAULT_TOKEN_WEIGHTS,
    ConfigKey,
)
from subsearch.ui.cards.base import SettingsCard
from subsearch.ui.cards.descriptions import SETTING_DESCRIPTIONS, CardKey
from subsearch.ui.icons.lucide import LucideIcon, lucide_qicon
from subsearch.ui.state.store import SettingsStore
from subsearch.ui.theme.metrics import CARD_CONTENT_INSET, ROW_INSET
from subsearch.ui.theme.separators import make_fading_separator
from subsearch.ui.theme.typography import (
    DISABLED_TEXT_COLOR,
    ERROR_TEXT_COLOR,
    SUCCESS_TEXT_COLOR,
    TEXT_COLOR,
    apply_body_font,
    apply_caption_font,
    apply_token_header_font,
    apply_token_row_label_font,
)
from subsearch.ui.widgets.setting_rows import (
    DefaultsMap,
    FloatInput,
    FuzzySelectRow,
    HelpButton,
    IntInput,
    IntInputRow,
    SwitchRow,
)
from subsearch.ui.widgets.slider import SliderWithValueLabel, track_aligned_label

_TOKEN_TUNING_DEFAULTS: DefaultsMap = [
    (ConfigKey.SEARCH_ACCEPT_THRESHOLD, 90),
    *((f"search.token_weights.{name}", default) for name, default in DEFAULT_TOKEN_WEIGHTS.items()),
    *((f"search.token_multipliers.{name}", default) for name, default in DEFAULT_TOKEN_MULTIPLIERS.items()),
]

PROVIDER_GRID_COLUMNS = 3

SUBSOURCE_PROVIDER_KEY = Provider.SUBSOURCE.value


class SearchModeCard(SettingsCard):
    def __init__(self, store: SettingsStore, parent: QWidget | None = None) -> None:
        super().__init__("Search mode", store, parent=parent)
        self.add_header_help(SETTING_DESCRIPTIONS[ConfigKey.SUBTITLE_WORKSPACE_SEARCH_MODE].explanation)
        search_mode_values = {"Manual": "manual", "Automatic": "automatic"}
        self.add_row(
            FuzzySelectRow(ConfigKey.SUBTITLE_WORKSPACE_SEARCH_MODE, store, search_mode_values, searchable=False)
        )
        visibility_values = {"Always": "always", "On attention required": "attention_required", "Never": "never"}
        self._visibility_row = FuzzySelectRow(
            ConfigKey.SUBTITLE_WORKSPACE_UI_VISIBILITY, store, visibility_values, searchable=False
        )
        self.add_row(self._visibility_row)
        self.register_restore_defaults(
            [
                (ConfigKey.SUBTITLE_WORKSPACE_SEARCH_MODE, "automatic"),
                (ConfigKey.SUBTITLE_WORKSPACE_UI_VISIBILITY, "attention_required"),
            ]
        )
        self._apply_visibility_enabled(store.read(ConfigKey.SUBTITLE_WORKSPACE_SEARCH_MODE))
        store.subscribe(ConfigKey.SUBTITLE_WORKSPACE_SEARCH_MODE, self._apply_visibility_enabled)

    def _apply_visibility_enabled(self, search_mode: str) -> None:
        # Visibility only applies to automatic; manual always opens the workspace.
        self._visibility_row.setEnabled(search_mode != "manual")


class LanguageCard(SettingsCard):
    def __init__(self, store: SettingsStore, parent: QWidget | None = None) -> None:
        super().__init__("Language", show_restore_button=False, parent=parent)
        languages = store.language_data()
        labelled_values = {data["name"]: key for key, data in languages.items()}
        aliases_by_label = {
            data["name"]: [code for code in (data["two_letter_code"], data["three_letter_code"]) if code]
            for data in languages.values()
        }
        self.add_header_help(SETTING_DESCRIPTIONS[ConfigKey.LANGUAGE_SELECTED].explanation)
        self.language_row = FuzzySelectRow(
            ConfigKey.LANGUAGE_SELECTED, store, labelled_values, aliases_by_label, show_help=False
        )
        self.add_row(self.language_row)


class SubtitleFiltersCard(SettingsCard):
    def __init__(self, store: SettingsStore, parent: QWidget | None = None) -> None:
        super().__init__("Subtitle filters", store, parent=parent)
        self.add_header_help(SETTING_DESCRIPTIONS[CardKey.SUBTITLE_FILTERS].explanation)
        self.add_row(SwitchRow(ConfigKey.SEARCH_HEARING_IMPAIRED, store))
        self.add_row(SwitchRow(ConfigKey.SEARCH_NON_HEARING_IMPAIRED, store))
        self.add_row(SwitchRow(ConfigKey.SEARCH_ONLY_FOREIGN_PARTS, store))


EXAMPLE_REFERENCE_MOVIE = "Shrek.2001.1080p.BluRay.x264-YOLO"
EXAMPLE_REFERENCE_SERIES = "Shrek.The.Shreky.s4e20.WEB.h264-DarkBrandon"
EXAMPLE_MOVIE_SUBTITLE = [
    "Shrek.2001.1080p.BluRay.x264-YOLO",
    "Shrek.2001.720p.WEBRip.x264-SwamP",
    "Shrek.1080p-L0vE",
    "Shrek.1969.1080p.BluRay.x264-YOLO",
]
EXAMPLE_SERIES_SUBTITLE = [
    "Shrek.The.Shreky.s4e20.WEB.h264-DarkBrandon",
    "Shrek.The.Shreky.s4e21.720p.HDTV.x264-YOLO",
    "Shrek.The.Shreky.s4e20.1969.DVDRip.x264-DarkBrandon",
    "Shrek.The.Shreky.s4e20",
]
VERDICT_ICON_SIZE = 16

TOKEN_WEIGHT_LABELS = {
    "title": "Title",
    "source": "Source",
    "group": "Release group",
}
TOKEN_MULTIPLIER_LABELS = {
    "year": "Year",
    "season_episode": "Season & episode",
    "edition": "Edition",
}

TOKEN_GRID_COLUMNS = 3

WEIGHT_ROW_LABEL = "Weight"
WEIGHT_MINIMUM = 0
WEIGHT_MAXIMUM = 100
MULTIPLIER_ROW_LABEL = "Mismatch multiplier"
MULTIPLIER_MINIMUM = 0.01
MULTIPLIER_MAXIMUM = 1.0
MULTIPLIER_DECIMALS = 2


EXAMPLE_ROW_HEIGHT = 22
SWAP_BUTTON_SIZE = 32


class ThresholdExampleRow(QWidget):
    def __init__(self, subtitle_name: str, left_inset: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._accepted: bool | None = None
        self.setFixedHeight(EXAMPLE_ROW_HEIGHT)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(left_inset, 2, CARD_CONTENT_INSET, 2)
        layout.setSpacing(12)

        name_label = CaptionLabel(subtitle_name, self)
        apply_caption_font(name_label)

        self.score_label = CaptionLabel("", self)
        apply_caption_font(self.score_label)
        self.score_label.setFixedWidth(44)
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self.verdict_icon = QLabel(self)
        self.verdict_icon.setFixedSize(VERDICT_ICON_SIZE, VERDICT_ICON_SIZE)

        self.verdict_label = CaptionLabel("", self)
        apply_caption_font(self.verdict_label)
        self.verdict_label.setFixedWidth(72)

        layout.addWidget(name_label, stretch=1)
        layout.addWidget(self.score_label)
        layout.addWidget(self.verdict_icon)
        layout.addWidget(self.verdict_label)

    def render_verdict(self, score: int, accepted: bool) -> None:
        color = SUCCESS_TEXT_COLOR if accepted else ERROR_TEXT_COLOR
        icon = LucideIcon.CIRCLE_CHECK_BIG if accepted else LucideIcon.CIRCLE_X
        self.score_label.setText(f"{score} %")
        self.verdict_icon.setPixmap(lucide_qicon(icon, color).pixmap(VERDICT_ICON_SIZE, VERDICT_ICON_SIZE))
        self.verdict_label.setText("Accepted" if accepted else "Rejected")
        if accepted != self._accepted:
            self._accepted = accepted
            self.verdict_label.setStyleSheet(f"color: {color};")


class TokenWeightCell(QWidget):
    value_changed = Signal()

    def __init__(self, config_key: str, store: SettingsStore, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.config_key = config_key
        self.store = store

        self.input = IntInput(WEIGHT_MINIMUM, WEIGHT_MAXIMUM, self)
        self.input.set_value_silent(int(store.read(config_key)))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.input, 0, Qt.AlignmentFlag.AlignHCenter)

        self.input.value_committed.connect(self._on_committed)
        store.value_changed.connect(self._on_store_changed)

    def value(self) -> int:
        return self.input.value()

    def _on_committed(self, value: int) -> None:
        self.store.write(self.config_key, value)
        self.value_changed.emit()

    def _on_store_changed(self, key: str, value: Any) -> None:
        if key != self.config_key:
            return
        self.input.set_value_silent(int(value))
        self.value_changed.emit()


class TokenMultiplierCell(QWidget):
    value_changed = Signal()

    def __init__(self, config_key: str, store: SettingsStore, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.config_key = config_key
        self.store = store

        self.input = FloatInput(MULTIPLIER_MINIMUM, MULTIPLIER_MAXIMUM, MULTIPLIER_DECIMALS, self)
        self.input.set_value_silent(float(store.read(config_key)))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.input, 0, Qt.AlignmentFlag.AlignHCenter)

        self.input.value_committed.connect(self._on_committed)
        store.value_changed.connect(self._on_store_changed)

    def value(self) -> float:
        return self.input.value()

    def _on_committed(self, value: float) -> None:
        self.store.write(self.config_key, value)
        self.value_changed.emit()

    def _on_store_changed(self, key: str, value: Any) -> None:
        if key != self.config_key:
            return
        self.input.set_value_silent(float(value))
        self.value_changed.emit()


class SearchThresholdCard(SettingsCard):
    def __init__(self, store: SettingsStore, parent: QWidget | None = None) -> None:
        super().__init__("Subtitle token filter", store, parent=parent)
        self.store = store
        self._using_series = False
        self.tuning_rows: dict[str, TokenWeightCell | TokenMultiplierCell] = {}
        self.register_restore_defaults(_TOKEN_TUNING_DEFAULTS)
        self._build_header()

        self._swap_button = TransparentToolButton(self)
        self._swap_button.setIconSize(QSize(16, 16))
        self._swap_button.setFixedSize(SWAP_BUTTON_SIZE, SWAP_BUTTON_SIZE)
        self._swap_button.clicked.connect(self._swap_examples)
        self._example_heading_spacing = 8
        self._example_left_inset = CARD_CONTENT_INSET + SWAP_BUTTON_SIZE + self._example_heading_spacing

        self.slider = SliderWithValueLabel(suffix="%", parent=self)
        self.slider.setRange(0, 100)
        self.slider.setValue(int(store.read(ConfigKey.SEARCH_ACCEPT_THRESHOLD)))

        self._build_examples()
        self._build_threshold_slider()
        self._build_token_tuning()

        self._write_timer = QTimer(self)
        self._write_timer.setSingleShot(True)
        self._write_timer.setInterval(400)
        self._write_timer.timeout.connect(self._on_slider_released)

        self._update_example_heading()
        self._refresh_examples()
        self.slider.valueChanged.connect(self._refresh_examples)
        self.slider.valueChanged.connect(lambda _: self._write_timer.start())
        self.slider.sliderReleased.connect(self._write_timer.stop)
        self.slider.sliderReleased.connect(self._on_slider_released)
        store.value_changed.connect(self._on_threshold_store_changed)

    def _build_header(self) -> None:
        self.add_header_help(SETTING_DESCRIPTIONS[ConfigKey.SEARCH_ACCEPT_THRESHOLD].explanation)

    def _build_examples(self) -> None:
        self._example_heading = CaptionLabel("", self)
        apply_caption_font(self._example_heading)
        self._example_heading.setStyleSheet(f"color: {TEXT_COLOR};")

        heading_row = QHBoxLayout()
        heading_row.setContentsMargins(CARD_CONTENT_INSET, 4, CARD_CONTENT_INSET, 0)
        heading_row.setSpacing(self._example_heading_spacing)
        heading_row.addWidget(self._swap_button, 0, Qt.AlignmentFlag.AlignVCenter)
        heading_row.addWidget(self._example_heading, stretch=1)
        self.body_layout.addLayout(heading_row)

        self._examples_start_index = self.body_layout.count()
        self.example_rows = [
            ThresholdExampleRow(name, self._example_left_inset, self) for name in EXAMPLE_MOVIE_SUBTITLE
        ]
        for row in self.example_rows:
            self.body_layout.addWidget(row)

    def _build_threshold_slider(self) -> None:
        slider_row = QHBoxLayout()
        slider_row.setContentsMargins(CARD_CONTENT_INSET, 10, ROW_INSET, 10)
        slider_row.setSpacing(12)
        slider_row.addWidget(track_aligned_label("Search threshold", self.slider, self))
        slider_row.addWidget(self.slider, stretch=1)
        slider_row.addWidget(
            HelpButton(SETTING_DESCRIPTIONS[ConfigKey.SEARCH_ACCEPT_THRESHOLD].explanation, self),
            alignment=Qt.AlignmentFlag.AlignVCenter,
        )
        self.body_layout.addLayout(slider_row)

    def _build_token_tuning(self) -> None:
        self.body_layout.addWidget(make_fading_separator(opacity=0.6, width_fraction=0.75, vertical_margin=12))
        grid = QGridLayout()
        grid.setContentsMargins(CARD_CONTENT_INSET, 4, ROW_INSET, 4)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(4)
        grid.setColumnStretch(0, 0)
        for column in range(1, TOKEN_GRID_COLUMNS + 1):
            grid.setColumnStretch(column, 1)
        grid.setColumnStretch(TOKEN_GRID_COLUMNS + 1, 0)

        self._add_token_grid_block(
            grid, 0, WEIGHT_ROW_LABEL, TOKEN_WEIGHT_LABELS, ConfigKey.SEARCH_TOKEN_WEIGHTS, TokenWeightCell
        )
        self._add_token_grid_block(
            grid,
            2,
            MULTIPLIER_ROW_LABEL,
            TOKEN_MULTIPLIER_LABELS,
            ConfigKey.SEARCH_TOKEN_MULTIPLIERS,
            TokenMultiplierCell,
        )
        self.body_layout.addLayout(grid)

    def _add_token_grid_block(
        self,
        grid: QGridLayout,
        header_row: int,
        row_label_text: str,
        token_labels: dict[str, str],
        key_prefix: ConfigKey,
        cell_type: type[TokenWeightCell] | type[TokenMultiplierCell],
    ) -> None:
        cell_row = header_row + 1

        row_label = CaptionLabel(row_label_text, self)
        apply_token_row_label_font(row_label)
        grid.addWidget(row_label, cell_row, 0, Qt.AlignmentFlag.AlignVCenter)

        for column, (token_name, token_text) in enumerate(token_labels.items(), start=1):
            header = CaptionLabel(token_text, self)
            apply_token_header_font(header)
            header.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            grid.addWidget(header, header_row, column, Qt.AlignmentFlag.AlignHCenter)
            cell = cell_type(f"{key_prefix}.{token_name}", self.store, self)
            cell.value_changed.connect(self._refresh_examples)
            self.tuning_rows[token_name] = cell
            grid.addWidget(cell, cell_row, column, Qt.AlignmentFlag.AlignHCenter)

        lamp = HelpButton(SETTING_DESCRIPTIONS[key_prefix].explanation, self)
        grid.addWidget(lamp, cell_row, TOKEN_GRID_COLUMNS + 1, Qt.AlignmentFlag.AlignVCenter)

    def _update_example_heading(self) -> None:
        reference = EXAMPLE_REFERENCE_SERIES if self._using_series else EXAMPLE_REFERENCE_MOVIE
        self._example_heading.setText(f"Live preview of {reference}.mkv")
        next_icon = LucideIcon.MONITOR if self._using_series else LucideIcon.TV
        tooltip = "Switch to movie example" if self._using_series else "Switch to series example"
        self._swap_button.setIcon(lucide_qicon(next_icon, TEXT_COLOR))
        self._swap_button.setToolTip(tooltip)

    def _swap_examples(self) -> None:
        self._using_series = not self._using_series
        subtitle_names = EXAMPLE_SERIES_SUBTITLE if self._using_series else EXAMPLE_MOVIE_SUBTITLE
        for row in self.example_rows:
            self.body_layout.removeWidget(row)
            row.deleteLater()
        self.example_rows = [ThresholdExampleRow(name, self._example_left_inset, self) for name in subtitle_names]
        for index, row in enumerate(self.example_rows):
            self.body_layout.insertWidget(self._examples_start_index + index, row)
            row.show()
        self._update_example_heading()
        self._refresh_examples()

    def _on_slider_released(self) -> None:
        self.store.write(ConfigKey.SEARCH_ACCEPT_THRESHOLD, self.slider.value())

    def _on_threshold_store_changed(self, key: str, value: Any) -> None:
        if key != ConfigKey.SEARCH_ACCEPT_THRESHOLD:
            return
        self.slider.set_value_silent(int(value))
        self._refresh_examples()

    def _refresh_examples(self) -> None:
        token_weights = self.store.read(ConfigKey.SEARCH_TOKEN_WEIGHTS)
        token_multipliers = self.store.read(ConfigKey.SEARCH_TOKEN_MULTIPLIERS)
        threshold = self.slider.value()
        reference = EXAMPLE_REFERENCE_SERIES if self._using_series else EXAMPLE_REFERENCE_MOVIE
        subtitle_names = EXAMPLE_SERIES_SUBTITLE if self._using_series else EXAMPLE_MOVIE_SUBTITLE
        for row, subtitle_name in zip(self.example_rows, subtitle_names):
            score = score_subtitle_tokens(reference, subtitle_name, token_weights, token_multipliers, log_match=False)
            row.render_verdict(score, score >= threshold)


class ProvidersCard(SettingsCard):
    def __init__(self, store: SettingsStore, parent: QWidget | None = None) -> None:
        super().__init__("Subtitle providers", show_restore_button=False, parent=parent)
        self.store = store
        provider_labels = PROVIDER_DISPLAY_NAMES
        self._language_data = store.language_data()
        providers = store.read(ConfigKey.SEARCH_PROVIDERS)
        self._help_button = self.add_header_help(SETTING_DESCRIPTIONS[ConfigKey.SEARCH_PROVIDERS].explanation)

        self.check_boxes: dict[str, CheckBox] = {}
        grid = QGridLayout()
        grid.setContentsMargins(CARD_CONTENT_INSET, 0, CARD_CONTENT_INSET, 10)
        grid.setHorizontalSpacing(24)
        grid.setVerticalSpacing(12)
        for column in range(PROVIDER_GRID_COLUMNS):
            grid.setColumnStretch(column, 1)
        for index, (provider_key, label) in enumerate(provider_labels.items()):
            row = index // PROVIDER_GRID_COLUMNS
            column = index % PROVIDER_GRID_COLUMNS
            check_box = CheckBox(label, self)
            apply_body_font(check_box)
            check_box.setChecked(bool(providers.get(provider_key, False)))
            check_box.toggled.connect(lambda checked, key=provider_key: self._on_provider_toggled(key, checked))
            grid.addWidget(check_box, row, column)
            self.check_boxes[provider_key] = check_box

        self.body_layout.addLayout(grid)

        self.add_row(IntInputRow(ConfigKey.SEARCH_DOWNLOADS_PER_PROVIDER, store, 1, 10))

        self._language_compatible: dict[str, bool] = {key: True for key in self.check_boxes}
        self._subsource_api_key_exists = bool(store.read(ConfigKey.CREDENTIALS_SUBSOURCE_API_KEY_EXISTS))

        self.apply_language_compatibility(store.read(ConfigKey.LANGUAGE_SELECTED))
        store.subscribe(ConfigKey.LANGUAGE_SELECTED, self.apply_language_compatibility)
        store.subscribe(ConfigKey.CREDENTIALS_SUBSOURCE_API_KEY_EXISTS, self._on_subsource_api_key_changed)
        store.value_changed.connect(self._on_store_changed)

    def _on_store_changed(self, key: str, value: Any) -> None:
        if key != ConfigKey.SEARCH_PROVIDERS:
            return
        for provider_key, check_box in self.check_boxes.items():
            check_box.blockSignals(True)
            check_box.setChecked(bool(value.get(provider_key, False)))
            check_box.blockSignals(False)

    def _on_provider_toggled(self, provider_key: str, checked: bool) -> None:
        providers = dict(self.store.read(ConfigKey.SEARCH_PROVIDERS))
        providers[provider_key] = checked
        self.store.write(ConfigKey.SEARCH_PROVIDERS, providers)

    def apply_language_compatibility(self, language: str) -> None:
        incompatible_providers = self._language_data.get(language, {}).get("incompatibility", [])
        for provider_key in self.check_boxes:
            self._language_compatible[provider_key] = provider_key not in incompatible_providers
            self._refresh_provider_enabled(provider_key)
        language_name = self._language_data.get(language, {}).get("name", language)
        self._help_button.set_explanation(
            SETTING_DESCRIPTIONS[ConfigKey.SEARCH_PROVIDERS].explanation.format(language=language_name)
        )

    def _on_subsource_api_key_changed(self, exists: bool) -> None:
        self._subsource_api_key_exists = bool(exists)
        self._refresh_provider_enabled(SUBSOURCE_PROVIDER_KEY)

    def _refresh_provider_enabled(self, provider_key: str) -> None:
        enabled = self._language_compatible[provider_key]
        if provider_key == SUBSOURCE_PROVIDER_KEY and not self._subsource_api_key_exists:
            enabled = False
        self._apply_provider_enabled_style(self.check_boxes[provider_key], enabled)

    def _apply_provider_enabled_style(self, check_box: CheckBox, enabled: bool) -> None:
        check_box.setEnabled(enabled)
        text_color = TEXT_COLOR if enabled else DISABLED_TEXT_COLOR
        check_box.setStyleSheet(f"CheckBox {{ color: {text_color}; }}")
