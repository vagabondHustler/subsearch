from typing import Any

from PySide6.QtCore import QSize, Qt, QTimer, Signal
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QVBoxLayout, QWidget
from qfluentwidgets import (
    CaptionLabel,
    CheckBox,
    TransparentToolButton,
)

from subsearch.parsing.release_parser import score_subtitle_tokens
from subsearch.runtime.config.static_values import (
    DEFAULT_TOKEN_MULTIPLIERS,
    DEFAULT_TOKEN_WEIGHTS,
)
from subsearch.ui.cards.base import SettingsCard
from subsearch.ui.cards.descriptions import SETTING_DESCRIPTIONS
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
    apply_token_value_font,
)
from subsearch.ui.widgets.setting_rows import (
    FloatInput,
    FuzzySelectRow,
    HelpButton,
    IntInput,
    SwitchRow,
)
from subsearch.ui.widgets.slider import SliderWithValueLabel, track_aligned_label

_TOKEN_TUNING_DEFAULTS: list[tuple[str, object]] = [
    ("search.accept_threshold", 90),
    *((f"search.token_weights.{name}", default) for name, default in DEFAULT_TOKEN_WEIGHTS.items()),
    *((f"search.token_multipliers.{name}", default) for name, default in DEFAULT_TOKEN_MULTIPLIERS.items()),
]

PROVIDER_GRID_COLUMNS = 3

PROVIDER_INCOMPATIBILITY_NAMES = {
    "opensubtitles": "opensubtitles",
    "yifysubtitles_site": "yifysubtitles",
    "subsource_site": "subsource",
}


class LanguageCard(SettingsCard):
    def __init__(self, store: SettingsStore, parent: QWidget | None = None) -> None:
        super().__init__("Language", show_restore_button=False, parent=parent)
        languages = store.language_data()
        labelled_values = {data["name"]: key for key, data in languages.items()}
        aliases_by_label = {
            data["name"]: [code for code in (data["two_letter_code"], data["three_letter_code"]) if code]
            for data in languages.values()
        }
        self.add_header_help(SETTING_DESCRIPTIONS["language.selected"].explanation)
        self.language_row = FuzzySelectRow(
            "language.selected", store, labelled_values, aliases_by_label, show_help=False
        )
        self.add_row(self.language_row)


class SubtitleFiltersCard(SettingsCard):
    def __init__(self, store: SettingsStore, parent: QWidget | None = None) -> None:
        super().__init__("Subtitle filters", store, parent=parent)
        self.add_header_help(SETTING_DESCRIPTIONS["card.subtitle_filters"].explanation)
        self.add_row(SwitchRow("search.hearing_impaired", store))
        self.add_row(SwitchRow("search.non_hearing_impaired", store))
        self.add_row(SwitchRow("search.only_foreign_parts", store))


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
        apply_token_value_font(self.input)

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
        apply_token_value_font(self.input)

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
        self.slider.setValue(int(store.read("search.accept_threshold")))

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
        self.add_header_help(SETTING_DESCRIPTIONS["search.accept_threshold"].explanation)

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
        slider_row.setContentsMargins(CARD_CONTENT_INSET, 10, CARD_CONTENT_INSET, 10)
        slider_row.setSpacing(12)
        slider_row.addWidget(track_aligned_label("Search threshold", self.slider, self))
        slider_row.addWidget(self.slider, stretch=1)
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
            grid, 0, WEIGHT_ROW_LABEL, TOKEN_WEIGHT_LABELS, "search.token_weights", TokenWeightCell
        )
        self._add_token_grid_block(
            grid, 2, MULTIPLIER_ROW_LABEL, TOKEN_MULTIPLIER_LABELS, "search.token_multipliers", TokenMultiplierCell
        )
        self.body_layout.addLayout(grid)

    def _add_token_grid_block(
        self,
        grid: QGridLayout,
        header_row: int,
        row_label_text: str,
        token_labels: dict[str, str],
        key_prefix: str,
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
        grid.addWidget(lamp, header_row, TOKEN_GRID_COLUMNS + 1, 2, 1, Qt.AlignmentFlag.AlignVCenter)

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
        self.store.write("search.accept_threshold", self.slider.value())

    def _on_threshold_store_changed(self, key: str, value: Any) -> None:
        if key != "search.accept_threshold":
            return
        self.slider.set_value_silent(int(value))
        self._refresh_examples()

    def _refresh_examples(self) -> None:
        token_weights = self.store.read("search.token_weights")
        token_multipliers = self.store.read("search.token_multipliers")
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
        provider_labels = {
            "opensubtitles": "Opensubtitles",
            "yifysubtitles_site": "Yifysubtitles",
            "subsource_site": "Subsource",
        }
        self._language_data = store.language_data()
        providers = store.read("search.providers")
        self._help_button = self.add_header_help(SETTING_DESCRIPTIONS["search.providers"].explanation)

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
            grid.addWidget(check_box, row, column, alignment=Qt.AlignmentFlag.AlignHCenter)
            self.check_boxes[provider_key] = check_box

        self.body_layout.addLayout(grid)

        self.apply_language_compatibility(store.read("language.selected"))
        store.subscribe("language.selected", self.apply_language_compatibility)
        store.value_changed.connect(self._on_store_changed)

    def _on_store_changed(self, key: str, value: Any) -> None:
        if key != "search.providers":
            return
        for provider_key, check_box in self.check_boxes.items():
            check_box.blockSignals(True)
            check_box.setChecked(bool(value.get(provider_key, False)))
            check_box.blockSignals(False)

    def _on_provider_toggled(self, provider_key: str, checked: bool) -> None:
        providers = dict(self.store.read("search.providers"))
        providers[provider_key] = checked
        self.store.write("search.providers", providers)

    def apply_language_compatibility(self, language: str) -> None:
        incompatible_providers = self._language_data.get(language, {}).get("incompatibility", [])
        for provider_key, check_box in self.check_boxes.items():
            compatible = PROVIDER_INCOMPATIBILITY_NAMES[provider_key] not in incompatible_providers
            self._apply_provider_compatibility_style(check_box, compatible)
        language_name = self._language_data.get(language, {}).get("name", language)
        self._help_button.set_explanation(
            SETTING_DESCRIPTIONS["search.providers"].explanation.format(language=language_name)
        )

    def _apply_provider_compatibility_style(self, check_box: CheckBox, compatible: bool) -> None:
        check_box.setEnabled(compatible)
        text_color = TEXT_COLOR if compatible else DISABLED_TEXT_COLOR
        check_box.setStyleSheet(f"CheckBox {{ color: {text_color}; }}")
