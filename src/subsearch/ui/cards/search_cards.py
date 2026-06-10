from PySide6.QtCore import QSize, Qt, QTimer, Signal
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QWidget
from qfluentwidgets import (
    CaptionLabel,
    CheckBox,
    SpinBox,
    TransparentToolButton,
)

from subsearch.parsing.release_parser import score_subtitle_tokens
from subsearch.runtime.config.static_values import (
    DEFAULT_TOKEN_MULTIPLIERS,
    DEFAULT_TOKEN_WEIGHTS,
)
from subsearch.ui.cards.base import SettingsCard
from subsearch.ui.cards.descriptions import SETTING_DESCRIPTIONS
from subsearch.ui.compat.qfluent import HANDLE_CENTER, HANDLE_SIZE, CircleDotSlider
from subsearch.ui.icons.lucide import LucideIcon, lucide_qicon
from subsearch.ui.state.store import SettingsStore
from subsearch.ui.theme.metrics import CARD_CONTENT_INSET
from subsearch.ui.theme.separators import make_fading_separator
from subsearch.ui.theme.typography import (
    DISABLED_TEXT_COLOR,
    ERROR_TEXT_COLOR,
    SUCCESS_TEXT_COLOR,
    TEXT_COLOR,
    apply_body_font,
    apply_caption_font,
)
from subsearch.ui.widgets.setting_rows import (
    SearchableComboBoxRow,
    SwitchRow,
)

_TOKEN_TUNING_DEFAULTS: list[tuple[str, object]] = [
    ("search.accept_threshold", 90),
    *(
        (f"search.token_weights.{name}", default)
        for name, default in DEFAULT_TOKEN_WEIGHTS.items()
    ),
    *(
        (f"search.token_multipliers.{name}", default)
        for name, default in DEFAULT_TOKEN_MULTIPLIERS.items()
    ),
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
        self.language_row = SearchableComboBoxRow(
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
    "group": "Release group",
    "source": "Source",
}
TOKEN_MULTIPLIER_LABELS = {
    "year": "Different year",
    "season_episode": "Different season or episode",
    "edition": "Different edition",
}


EXAMPLE_ROW_HEIGHT = 22


class ThresholdExampleRow(QWidget):
    def __init__(self, subtitle_name: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._accepted: bool | None = None
        self.setFixedHeight(EXAMPLE_ROW_HEIGHT)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(CARD_CONTENT_INSET, 2, CARD_CONTENT_INSET, 2)
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


class AdvancedTuningRow(QWidget):
    value_changed = Signal()

    def __init__(
        self, label_text: str, config_key: str, spin_box, store: SettingsStore, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.config_key = config_key
        self.store = store
        self.spin_box = spin_box
        apply_body_font(self.spin_box)
        self.spin_box.setFixedWidth(110)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(CARD_CONTENT_INSET, 2, CARD_CONTENT_INSET, 2)
        layout.setSpacing(12)
        label = CaptionLabel(label_text, self)
        apply_caption_font(label)
        layout.addWidget(label, stretch=1)
        layout.addWidget(self.spin_box)

        self.spin_box.valueChanged.connect(self._on_value_changed)
        store.value_changed.connect(self._on_store_changed)

    def _on_value_changed(self, value) -> None:
        self.store.write(self.config_key, value)
        self.value_changed.emit()

    def _on_store_changed(self, key: str, value: object) -> None:
        if key != self.config_key:
            return
        self.spin_box.blockSignals(True)
        self.spin_box.setValue(int(value))
        self.spin_box.blockSignals(False)
        self.value_changed.emit()

    def reset_to(self, value) -> None:
        self.spin_box.blockSignals(True)
        self.spin_box.setValue(value)
        self.spin_box.blockSignals(False)
        self.store.write(self.config_key, value)


class SliderWithValueLabel(QWidget):
    valueChanged = Signal(int)
    sliderReleased = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._slider = CircleDotSlider(Qt.Orientation.Horizontal, self)
        self._label = CaptionLabel("", self)
        apply_body_font(self._label)
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setFixedWidth(52)
        self._slider.valueChanged.connect(self._on_value_changed)
        self._slider.sliderReleased.connect(self.sliderReleased)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        label_h = self._label.sizeHint().height()
        self._slider.setGeometry(0, label_h + 4, self.width(), HANDLE_SIZE)
        self._update_label_pos()

    def sizeHint(self) -> QSize:
        label_h = self._label.sizeHint().height()
        return QSize(200, label_h + 4 + HANDLE_SIZE)

    def minimumSizeHint(self) -> QSize:
        return self.sizeHint()

    def _update_label_pos(self) -> None:
        if self._slider.width() == 0:
            return
        value = self._slider.value()
        minimum, maximum = self._slider.minimum(), self._slider.maximum()
        t = (value - minimum) / (maximum - minimum) if maximum > minimum else 0
        handle_center_x = HANDLE_CENTER + round(t * (self._slider.width() - HANDLE_SIZE))
        label_x = handle_center_x - self._label.width() // 2
        label_x = max(0, min(label_x, self.width() - self._label.width()))
        self._label.move(label_x, 0)

    def _on_value_changed(self, value: int) -> None:
        self._label.setText(f"{value} %")
        self._update_label_pos()
        self.valueChanged.emit(value)

    def setValue(self, value: int) -> None:
        self._slider.setValue(value)

    def set_value_silent(self, value: int) -> None:
        self._slider.set_value_silent(value)
        self._label.setText(f"{value} %")
        self._update_label_pos()

    def value(self) -> int:
        return self._slider.value()

    def setRange(self, minimum: int, maximum: int) -> None:
        self._slider.setRange(minimum, maximum)


class SearchThresholdCard(SettingsCard):
    def __init__(self, store: SettingsStore, parent: QWidget | None = None) -> None:
        super().__init__("Search threshold", store, parent=parent)
        self.store = store
        self._using_series = False
        self.tuning_rows: dict[str, AdvancedTuningRow] = {}
        self.register_restore_defaults(_TOKEN_TUNING_DEFAULTS)
        self._build_header()

        self._swap_button = TransparentToolButton(self)
        self._swap_button.setIconSize(QSize(16, 16))
        self._swap_button.setFixedSize(32, 32)
        self._swap_button.clicked.connect(self._swap_examples)

        self.slider = SliderWithValueLabel(self)
        self.slider.setRange(0, 100)
        self.slider.setValue(int(store.read("search.accept_threshold")))

        slider_row = QHBoxLayout()
        slider_row.setContentsMargins(CARD_CONTENT_INSET - HANDLE_CENTER, 6, CARD_CONTENT_INSET, 10)
        slider_row.setSpacing(0)
        slider_row.addWidget(self.slider)
        slider_row.addWidget(self._swap_button, 0, Qt.AlignmentFlag.AlignBottom)
        self.body_layout.addLayout(slider_row)

        self._build_examples()
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
        heading_row.addWidget(self._example_heading)
        self.body_layout.addLayout(heading_row)

        self._examples_start_index = self.body_layout.count()
        self.example_rows = [ThresholdExampleRow(name, self) for name in EXAMPLE_MOVIE_SUBTITLE]
        for row in self.example_rows:
            self.body_layout.addWidget(row)

    def _build_token_tuning(self) -> None:
        self.body_layout.addWidget(make_fading_separator(opacity=0.6, width_fraction=0.75, vertical_margin=6))
        self.body_layout.addWidget(self._heading("Weights"))
        for token_name, label_text in TOKEN_WEIGHT_LABELS.items():
            self.body_layout.addWidget(self._weight_row(token_name, label_text))
        self.body_layout.addWidget(self._heading("Mismatch penalties"))
        for token_name, label_text in TOKEN_MULTIPLIER_LABELS.items():
            self.body_layout.addWidget(self._multiplier_row(token_name, label_text))


    def _heading(self, text: str) -> CaptionLabel:
        heading = CaptionLabel(text, self)
        apply_caption_font(heading)
        heading.setContentsMargins(CARD_CONTENT_INSET, 4, CARD_CONTENT_INSET, 0)
        heading.setStyleSheet(f"color: {TEXT_COLOR};")
        return heading

    def _weight_row(self, token_name: str, label_text: str) -> AdvancedTuningRow:
        config_key = f"search.token_weights.{token_name}"
        return self._tuning_row(token_name, label_text, config_key)

    def _multiplier_row(self, token_name: str, label_text: str) -> AdvancedTuningRow:
        config_key = f"search.token_multipliers.{token_name}"
        return self._tuning_row(token_name, label_text, config_key)

    def _tuning_row(self, token_name: str, label_text: str, config_key: str) -> AdvancedTuningRow:
        spin_box = SpinBox()
        spin_box.setRange(0, 100)
        spin_box.setValue(int(self.store.read(config_key)))
        row = AdvancedTuningRow(label_text, config_key, spin_box, self.store, self)
        row.value_changed.connect(self._refresh_examples)
        self.tuning_rows[token_name] = row
        return row

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
        self.example_rows = [ThresholdExampleRow(name, self) for name in subtitle_names]
        for index, row in enumerate(self.example_rows):
            self.body_layout.insertWidget(self._examples_start_index + index, row)
            row.show()
        self._update_example_heading()
        self._refresh_examples()

    def _on_slider_released(self) -> None:
        self.store.write("search.accept_threshold", self.slider.value())

    def _on_threshold_store_changed(self, key: str, value: object) -> None:
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
            score = score_subtitle_tokens(reference, subtitle_name, token_weights, token_multipliers)
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

    def _on_provider_toggled(self, provider_key: str, checked: bool) -> None:
        providers = self.store.read("search.providers")
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
