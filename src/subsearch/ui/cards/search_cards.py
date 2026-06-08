from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QWidget
from qfluentwidgets import CaptionLabel, CheckBox

from subsearch.io import toml_file
from subsearch.ui.cards.base import SettingsCard
from subsearch.ui.cards.descriptions import SETTING_DESCRIPTIONS
from subsearch.ui.theme.typography import (
    DISABLED_TEXT_COLOR,
    TEXT_COLOR,
    apply_body_font,
)
from subsearch.ui.widgets.setting_rows import (
    SearchableComboBoxRow,
    SwitchRow,
    read_value,
    write_value,
)
from subsearch.ui.widgets.slider import CircleDotSlider

PROVIDER_GRID_COLUMNS = 3

PROVIDER_INCOMPATIBILITY_NAMES = {
    "opensubtitles": "opensubtitles",
    "yifysubtitles_site": "yifysubtitles",
    "subsource_site": "subsource",
}


class LanguageCard(SettingsCard):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Language", parent)
        languages = toml_file.load_language_data()
        labelled_values = {data["name"]: key for key, data in languages.items()}
        aliases_by_label = {
            data["name"]: [code for code in (data["two_letter_code"], data["three_letter_code"]) if code]
            for data in languages.values()
        }
        self.add_header_help(SETTING_DESCRIPTIONS["language.selected"].explanation)
        self.language_row = SearchableComboBoxRow(
            "language.selected", labelled_values, aliases_by_label, show_help=False
        )
        self.add_row(self.language_row)

    @property
    def selection_changed(self):
        return self.language_row.selection_changed


class SubtitleFiltersCard(SettingsCard):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Subtitle filters", parent)
        self.add_row(SwitchRow("search.hearing_impaired"))
        self.add_row(SwitchRow("search.non_hearing_impaired"))
        self.add_row(SwitchRow("search.only_foreign_parts"))


class SearchThresholdCard(SettingsCard):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Search threshold", parent)
        self.add_header_help(SETTING_DESCRIPTIONS["search.accept_threshold"].explanation)

        self.value_label = CaptionLabel("", self)
        apply_body_font(self.value_label)
        value_row = QHBoxLayout()
        value_row.setContentsMargins(16, 6, 16, 0)
        value_row.addStretch(1)
        value_row.addWidget(self.value_label)
        value_row.addStretch(1)
        self.body_layout.addLayout(value_row)

        self.slider = CircleDotSlider(Qt.Orientation.Horizontal, self)
        self.slider.setRange(0, 100)
        self.slider.setValue(int(read_value("search.accept_threshold")))
        slider_row = QHBoxLayout()
        slider_row.setContentsMargins(48, 0, 48, 10)
        slider_row.addWidget(self.slider)
        self.body_layout.addLayout(slider_row)

        self._update_value_label(self.slider.value())
        self.slider.valueChanged.connect(self._on_value_changed)

    def _on_value_changed(self, value: int) -> None:
        self._update_value_label(value)
        write_value("search.accept_threshold", value)

    def _update_value_label(self, value: int) -> None:
        self.value_label.setText(f"{value} %")


class ProvidersCard(SettingsCard):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Subtitle providers", parent)
        provider_labels = {
            "opensubtitles": "Opensubtitles",
            "yifysubtitles_site": "Yifysubtitles",
            "subsource_site": "Subsource",
        }
        self._language_data = toml_file.load_language_data()
        providers = read_value("search.providers")
        self._help_button = self.add_header_help(SETTING_DESCRIPTIONS["search.providers"].explanation)

        self.check_boxes: dict[str, CheckBox] = {}
        grid = QGridLayout()
        grid.setContentsMargins(48, 0, 48, 10)
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

        self.apply_language_compatibility(read_value("language.selected"))

    def _on_provider_toggled(self, provider_key: str, checked: bool) -> None:
        providers = read_value("search.providers")
        providers[provider_key] = checked
        write_value("search.providers", providers)

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
