import webbrowser
from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor, QKeyEvent, QKeySequence, QPainter
from PySide6.QtWidgets import QFileDialog, QGridLayout, QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import (
    BodyLabel,
    CaptionLabel,
    CheckBox,
    HeaderCardWidget,
    LineEdit,
    MessageBox,
    TransparentToolButton,
)

from subsearch.io import toml_file, windows_registry
from subsearch.parsing import release_parser
from subsearch.runtime.constants import DEVICE_INFO, FILE_PATHS
from subsearch.ui.cards.descriptions import SETTING_DESCRIPTIONS
from subsearch.ui.icons.lucide import LucideIcon, lucide_qicon
from subsearch.ui.theme.separators import make_fading_separator
from subsearch.ui.widgets.slider import CircleDotSlider
from subsearch.ui.widgets.setting_rows import (
    ComboBoxRow,
    HelpButton,
    SearchableComboBoxRow,
    SpinBoxRow,
    SwitchRow,
    read_value,
    write_value,
)
from subsearch.ui.theme.typography import (
    DISABLED_TEXT_COLOR,
    TEXT_COLOR,
    apply_body_font,
    apply_caption_font,
    apply_title_font,
)

EXTENSION_GRID_ROWS = 3
PROVIDER_GRID_COLUMNS = 3
VISIBLE_PREFIX_LENGTH = 4
MASK_CHARACTER = "•"
REVEAL_ICON_SIZE = 18
REVEAL_BUTTON_SIZE = 32
LINK_BUTTON_ICON_SIZE = 24
LINK_BUTTON_SIZE = 32
LINK_BUTTON_SPACING = 48
API_KEY_CONFIG_KEY = "credentials.subsource_api_key"
REQUEST_LIMITS_KEY = "credentials.subsource_request_limits"
GETTING_API_KEY_KEY = "credentials.subsource_getting_api_key"
PROFILE_URL = "https://subsource.net/dashboard/profile"
API_DOCS_URL = "https://subsource.net/api-docs"
DEFAULT_TARGET_PATH = "."
DEFAULT_PATH_RESOLUTION = "relative"
DESTINATION_PATH_EXAMPLES = (
    "Where moved subtitles are placed.\n\n"
    "Relative — taken from the video's own folder:\n"
    "    subs\n"
    "    ..\\Subtitles\n\n"
    "Absolute — a fixed path on disk:\n"
    "    C:\\Users\\You\\Subtitles\n"
    "    D:\\Media\\Subs"
)


def build_section_header(config_key: str, parent: QWidget) -> QHBoxLayout:
    description = SETTING_DESCRIPTIONS[config_key]
    title_label = BodyLabel(description.title, parent)
    apply_body_font(title_label)
    help_button = HelpButton(description.explanation, parent)
    header = QHBoxLayout()
    header.setContentsMargins(16, 10, 16, 4)
    header.addWidget(title_label, stretch=1)
    header.addWidget(help_button)
    return header


def mask_api_key(api_key: str) -> str:
    if len(api_key) <= VISIBLE_PREFIX_LENGTH:
        return MASK_CHARACTER * len(api_key)
    hidden_length = len(api_key) - VISIBLE_PREFIX_LENGTH
    return api_key[:VISIBLE_PREFIX_LENGTH] + MASK_CHARACTER * hidden_length


CARD_PANEL_OPACITY = 0.4
CARD_FILL_COLOR = QColor(255, 255, 255, 13)
CARD_BORDER_COLOR = QColor(0, 0, 0, 48)
CARD_BORDER_RADIUS = 6.0


class SettingsCard(HeaderCardWidget):
    def __init__(  # pyright: ignore[reportIncompatibleVariableOverride]
        self, title: str, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setTitle(title)
        apply_title_font(self.headerLabel)
        self._replace_header_separator()
        self.headerLayout.setContentsMargins(16, 0, 16, 0)
        self.viewLayout.setContentsMargins(0, 8, 0, 8)
        self.body_layout = QVBoxLayout()
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(4)
        self.viewLayout.addLayout(self.body_layout)

    def paintEvent(self, e) -> None:
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)
        painter.setOpacity(CARD_PANEL_OPACITY)
        painter.setBrush(CARD_FILL_COLOR)
        painter.setPen(CARD_BORDER_COLOR)
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), CARD_BORDER_RADIUS, CARD_BORDER_RADIUS)

    def enterEvent(self, e) -> None:
        pass

    def leaveEvent(self, e) -> None:
        pass

    def _replace_header_separator(self) -> None:
        index = self.vBoxLayout.indexOf(self.separator)
        self.separator.hide()
        self.vBoxLayout.removeWidget(self.separator)
        self.vBoxLayout.insertWidget(index, make_fading_separator())

    def add_row(self, widget: QWidget) -> None:
        self.body_layout.addWidget(widget)

    def add_header_help(self, explanation: str) -> HelpButton:
        self.headerLayout.addStretch(1)
        help_button = HelpButton(explanation, self)
        self.headerLayout.addWidget(help_button)
        return help_button


class LanguageCard(SettingsCard):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Language", parent)
        languages = toml_file.load_toml_data(FILE_PATHS.subtitle_languages)
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


PROVIDER_INCOMPATIBILITY_NAMES = {
    "opensubtitles": "opensubtitles",
    "yifysubtitles_site": "yifysubtitles",
    "subsource_site": "subsource",
}


class ProvidersCard(SettingsCard):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Subtitle providers", parent)
        provider_labels = {
            "opensubtitles": "Opensubtitles",
            "yifysubtitles_site": "Yifysubtitles",
            "subsource_site": "Subsource",
        }
        self._language_data = toml_file.load_toml_data(FILE_PATHS.subtitle_languages)
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
            self._set_provider_compatible(check_box, compatible)
        language_name = self._language_data.get(language, {}).get("name", language)
        self._help_button.set_explanation(
            SETTING_DESCRIPTIONS["search.providers"].explanation.format(language=language_name)
        )

    def _set_provider_compatible(self, check_box: CheckBox, compatible: bool) -> None:
        check_box.setEnabled(compatible)
        text_color = TEXT_COLOR if compatible else DISABLED_TEXT_COLOR
        check_box.setStyleSheet(f"CheckBox {{ color: {text_color}; }}")


class PostProcessingCard(SettingsCard):
    mutually_exclusive_keys = {"post_processing.move_best", "post_processing.move_all"}

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Subtitle post-processing", parent)
        self.add_row(SwitchRow("post_processing.rename"))
        self.move_best = SwitchRow("post_processing.move_best")
        self.move_all = SwitchRow("post_processing.move_all")
        self.add_row(self.move_best)
        self.add_row(self.move_all)
        self.move_best.toggled.connect(self._on_move_toggled)
        self.move_all.toggled.connect(self._on_move_toggled)

        self._build_destination()
        self._update_destination_enabled()

    def _on_move_toggled(self, checked: bool) -> None:
        toggled_row = self.sender()
        other_row = self.move_all if toggled_row is self.move_best else self.move_best
        self._enforce_mutual_exclusivity(other_row, checked)
        self._update_destination_enabled()

    def _enforce_mutual_exclusivity(self, other_row: SwitchRow, enabled: bool) -> None:
        if enabled and other_row.switch.isChecked():
            other_row.set_checked_silently(False)

    def _update_destination_enabled(self) -> None:
        moving_enabled = self.move_best.switch.isChecked() or self.move_all.switch.isChecked()
        self.destination.setEnabled(moving_enabled)

    def _build_destination(self) -> None:
        self.destination = QWidget(self)
        destination_layout = QVBoxLayout(self.destination)
        destination_layout.setContentsMargins(0, 0, 0, 0)
        destination_layout.addLayout(build_section_header("post_processing.target_path", self))

        self.path_edit = LineEdit(self)
        self.path_edit.setText(str(read_value("post_processing.target_path")))
        self.path_edit.setClearButtonEnabled(True)
        apply_body_font(self.path_edit)
        self.path_edit.textChanged.connect(self._on_path_text_changed)
        self.path_edit.editingFinished.connect(self._save_path_if_valid)
        help_button = HelpButton(DESTINATION_PATH_EXAMPLES, self)
        path_row = QHBoxLayout()
        path_row.setContentsMargins(16, 0, 16, 10)
        path_row.addWidget(self.path_edit, stretch=1)
        path_row.addWidget(self._build_browse_button())
        path_row.addWidget(help_button)
        destination_layout.addLayout(path_row)

        destination_layout.addWidget(SwitchRow("post_processing.create_missing_folder", self))
        self.body_layout.addWidget(self.destination)

    def _build_browse_button(self) -> QWidget:
        browse_button = TransparentToolButton(lucide_qicon(LucideIcon.FOLDER_OPEN, TEXT_COLOR), self)
        browse_button.setFixedSize(32, 32)
        browse_button.setIconSize(QSize(24, 24))
        browse_button.clicked.connect(self._browse_for_folder)
        caption = CaptionLabel("Browse", self)
        apply_caption_font(caption)
        caption.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        container = QWidget(self)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        container_layout.addWidget(browse_button, alignment=Qt.AlignmentFlag.AlignHCenter)
        container_layout.addWidget(caption)
        return container

    def _browse_for_folder(self) -> None:
        selected_folder = QFileDialog.getExistingDirectory(
            self.window(),
            "Select destination folder",
            self.path_edit.text(),
        )
        if not selected_folder:
            return
        self.path_edit.setText(str(Path(selected_folder)))
        self._save_path_if_valid()

    def _set_path_error(self, is_error: bool) -> None:
        self.path_edit.setError(is_error)
        self.path_edit.setProperty("error", "true" if is_error else "false")
        self.path_edit.style().unpolish(self.path_edit)
        self.path_edit.style().polish(self.path_edit)

    def _path_is_valid(self) -> bool:
        target_path = self.path_edit.text()
        path_resolution = release_parser.detect_path_resolution(target_path)
        return release_parser.valid_path(target_path, path_resolution)

    def _persist_path(self) -> None:
        target_path = self.path_edit.text()
        path_resolution = release_parser.detect_path_resolution(target_path)
        self._set_path_error(False)
        write_value("post_processing.target_path", target_path)
        write_value("post_processing.path_resolution", path_resolution)

    def _save_path_if_valid(self) -> None:
        if self._path_is_valid():
            self._persist_path()

    def commit_path_or_revert(self) -> bool:
        if self._path_is_valid():
            self._persist_path()
            return True
        return self._prompt_invalid_path_on_exit()

    def _prompt_invalid_path_on_exit(self) -> bool:
        confirmation = MessageBox(
            "Destination folder is not valid",
            f'The destination folder\n\n"{self.path_edit.text()}"\n\nis not valid. '
            f'Exit anyway and reset it to the default ("{DEFAULT_TARGET_PATH}"), '
            "or stay and fix it?",
            self.window(),
        )
        confirmation.yesButton.setText("Reset and exit")
        confirmation.cancelButton.setText("Stay and fix")
        if not confirmation.exec():
            return False
        self.path_edit.setText(DEFAULT_TARGET_PATH)
        write_value("post_processing.target_path", DEFAULT_TARGET_PATH)
        write_value("post_processing.path_resolution", DEFAULT_PATH_RESOLUTION)
        return True

    def _on_path_text_changed(self, target_path: str) -> None:
        path_resolution = release_parser.detect_path_resolution(target_path)
        self._set_path_error(not release_parser.valid_path(target_path, path_resolution))


class FileExtensionsCard(SettingsCard):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("File extensions", parent)
        self.add_header_help(SETTING_DESCRIPTIONS["shell_integration.file_extensions"].explanation)

        file_extensions = read_value("shell_integration.file_extensions")
        self.check_boxes: dict[str, CheckBox] = {}
        grid = QGridLayout()
        grid.setContentsMargins(48, 0, 48, 10)
        grid.setHorizontalSpacing(24)
        grid.setVerticalSpacing(12)
        column_count = -(-len(file_extensions) // EXTENSION_GRID_ROWS)
        for column in range(column_count):
            grid.setColumnStretch(column, 1)
        for index, (extension, enabled) in enumerate(file_extensions.items()):
            row = index % EXTENSION_GRID_ROWS
            column = index // EXTENSION_GRID_ROWS
            check_box = CheckBox(extension, self)
            apply_body_font(check_box)
            check_box.setChecked(bool(enabled))
            check_box.toggled.connect(lambda checked, ext=extension: self._on_extension_toggled(ext, checked))
            grid.addWidget(check_box, row, column, alignment=Qt.AlignmentFlag.AlignLeft)
            self.check_boxes[extension] = check_box

        self.body_layout.addLayout(grid)

    def _on_extension_toggled(self, extension: str, checked: bool) -> None:
        file_extensions = read_value("shell_integration.file_extensions")
        file_extensions[extension] = checked
        write_value("shell_integration.file_extensions", file_extensions)
        if read_value("shell_integration.context_menu"):
            windows_registry.write_all_valuex()

    def set_enabled(self, enabled: bool) -> None:
        for check_box in self.check_boxes.values():
            check_box.setEnabled(enabled)


class ShellIntegrationCard(SettingsCard):
    def __init__(self, file_extensions_card: FileExtensionsCard, parent: QWidget | None = None) -> None:
        super().__init__("Shell integration", parent)
        self.file_extensions_card = file_extensions_card

        self.context_menu = SwitchRow("shell_integration.context_menu")
        self.context_menu_icon = SwitchRow("shell_integration.context_menu_icon")
        self.add_row(self.context_menu)
        self.add_row(self.context_menu_icon)
        self.context_menu.toggled.connect(self._on_context_menu_toggled)
        self.context_menu_icon.toggled.connect(self._on_context_menu_icon_toggled)
        self._apply_context_menu_state(self.context_menu.switch.isChecked())

    def _on_context_menu_toggled(self, enabled: bool) -> None:
        if enabled:
            windows_registry.add_context_menu()
        else:
            windows_registry.del_context_menu()
        self._apply_context_menu_state(enabled)

    def _on_context_menu_icon_toggled(self) -> None:
        if read_value("shell_integration.context_menu"):
            windows_registry.write_all_valuex()

    def _apply_context_menu_state(self, enabled: bool) -> None:
        self.context_menu_icon.set_enabled(enabled)
        self.file_extensions_card.set_enabled(enabled)


class NotificationsCard(SettingsCard):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Notifications", parent)
        self.system_tray = SwitchRow("notifications.system_tray")
        self.summary_notification = SwitchRow("notifications.summary_notification")
        self.add_row(self.system_tray)
        self.add_row(self.summary_notification)
        self.system_tray.toggled.connect(self.summary_notification.set_enabled)
        self.summary_notification.set_enabled(self.system_tray.switch.isChecked())


class DownloadManagerCard(SettingsCard):
    mutually_exclusive_keys = {
        "download.open_manager_on_no_matches",
        "download.always_open_manager",
    }

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Download manager", parent)
        self.add_row(SwitchRow("download.automatic"))
        self.open_on_no_matches = SwitchRow("download.open_manager_on_no_matches")
        self.always_open = SwitchRow("download.always_open_manager")
        self.add_row(self.open_on_no_matches)
        self.add_row(self.always_open)
        self.open_on_no_matches.toggled.connect(
            lambda checked: self._enforce_mutual_exclusivity(self.always_open, checked)
        )
        self.always_open.toggled.connect(
            lambda checked: self._enforce_mutual_exclusivity(self.open_on_no_matches, checked)
        )

    def _enforce_mutual_exclusivity(self, other_row: SwitchRow, enabled: bool) -> None:
        if enabled and other_row.switch.isChecked():
            other_row.set_checked_silently(False)


class ApplicationCard(SettingsCard):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Application", parent)
        show_terminal = SwitchRow("application.show_terminal")
        if DEVICE_INFO.mode == "executable":
            show_terminal.set_enabled(False)
        self.add_row(show_terminal)
        self.add_row(SwitchRow("application.single_instance"))


class NetworkCard(SettingsCard):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Network", parent)
        self.add_row(SpinBoxRow("network.api_call_limit", 1, 99))
        self.add_row(SpinBoxRow("network.request_connect_timeout", 1, 99))
        self.add_row(SpinBoxRow("network.request_read_timeout", 1, 99))


class ProviderHealthCard(SettingsCard):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Provider health", parent)
        self.enabled = SwitchRow("diagnostics.enabled")
        self.run_when = ComboBoxRow(
            "diagnostics.run_when",
            {"After search": "after_search", "On launch": "on_launch"},
        )
        self.interval = SpinBoxRow("diagnostics.interval_days", 1, 24)
        self.add_row(self.enabled)
        self.add_row(self.run_when)
        self.add_row(self.interval)
        self.enabled.toggled.connect(self._apply_enabled_state)
        self._apply_enabled_state(self.enabled.switch.isChecked())

    def _apply_enabled_state(self, enabled: bool) -> None:
        self.run_when.setEnabled(enabled)
        self.interval.setEnabled(enabled)


class MaskedApiKeyLineEdit(LineEdit):
    def __init__(self, api_key: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._api_key = api_key
        self._revealed = False
        self.setPlaceholderText("sk_...")
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.setCursor(Qt.CursorShape.IBeamCursor)
        self._render()

    @property
    def api_key(self) -> str:
        return self._api_key

    def set_revealed(self, revealed: bool) -> None:
        self._revealed = revealed
        self._render()

    def _render(self) -> None:
        self.blockSignals(True)
        super().setText(self._api_key if self._revealed else mask_api_key(self._api_key))
        self.deselect()
        self.end(False)
        self.blockSignals(False)

    def _set_api_key(self, api_key: str) -> None:
        if api_key == self._api_key:
            return
        self._api_key = api_key
        self._render()
        self.api_key_changed()

    def api_key_changed(self) -> None: ...

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.matches(QKeySequence.StandardKey.Paste) or event.matches(QKeySequence.StandardKey.Copy):
            event.ignore()
            return
        if event.key() in (Qt.Key.Key_Backspace, Qt.Key.Key_Delete):
            self._set_api_key(self._api_key[:-1])
            return
        if event.text() and event.text().isprintable():
            self._set_api_key(self._api_key + event.text())
            return
        event.ignore()

    def mousePressEvent(self, event) -> None:
        self.setFocus()
        event.accept()

    def mouseMoveEvent(self, event) -> None:
        event.accept()

    def mouseDoubleClickEvent(self, event) -> None:
        event.accept()


class ApiKeyField(QWidget):
    def __init__(self, config_key: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.config_key = config_key
        api_key = str(read_value(config_key))

        self.line_edit = MaskedApiKeyLineEdit(api_key, self)
        apply_body_font(self.line_edit)
        self.line_edit.api_key_changed = self._on_api_key_changed

        self._revealed = False
        self.reveal_button = TransparentToolButton(self)
        self.reveal_button.setFixedSize(REVEAL_BUTTON_SIZE, REVEAL_BUTTON_SIZE)
        self.reveal_button.setIconSize(QSize(REVEAL_ICON_SIZE, REVEAL_ICON_SIZE))
        self.reveal_button.clicked.connect(self._toggle_revealed)
        self._apply_reveal_icon()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 4, 16, 8)
        layout.setSpacing(8)
        layout.addWidget(self.line_edit, stretch=1)
        layout.addWidget(self.reveal_button)

        self._apply_validation_state(api_key)

    def _toggle_revealed(self) -> None:
        self._revealed = not self._revealed
        self.line_edit.set_revealed(self._revealed)
        self._apply_reveal_icon()

    def _apply_reveal_icon(self) -> None:
        icon = LucideIcon.EYE_OFF if self._revealed else LucideIcon.EYE
        self.reveal_button.setIcon(lucide_qicon(icon, TEXT_COLOR))

    def _on_api_key_changed(self) -> None:
        api_key = self.line_edit.api_key
        write_value(self.config_key, api_key)
        self._apply_validation_state(api_key)

    def _apply_validation_state(self, api_key: str) -> None:
        is_error = bool(api_key) and not release_parser.valid_subsource_api_key(api_key)
        self.line_edit.setError(is_error)


class ApiCard(SettingsCard):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Subsource", parent)
        self.add_header_help(SETTING_DESCRIPTIONS[API_KEY_CONFIG_KEY].explanation)

        title_label = BodyLabel("API key", self)
        apply_body_font(title_label)
        title_row = QHBoxLayout()
        title_row.setContentsMargins(16, 6, 16, 0)
        title_row.addWidget(title_label)
        self.body_layout.addLayout(title_row)

        self.add_row(ApiKeyField(API_KEY_CONFIG_KEY, self))
        self.body_layout.addWidget(self._build_request_limits())
        self.body_layout.addWidget(self._build_getting_started())

    def _build_request_limits(self) -> QWidget:
        container, _ = self._build_text_block(REQUEST_LIMITS_KEY)
        return container

    def _build_text_block(self, description_key: str) -> tuple[QWidget, QVBoxLayout]:
        description = SETTING_DESCRIPTIONS[description_key]
        container = QWidget(self)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 4, 16, 8)
        layout.setSpacing(6)

        title_label = BodyLabel(description.title, self)
        apply_body_font(title_label)
        layout.addWidget(title_label)

        body_label = CaptionLabel(description.explanation, self)
        apply_caption_font(body_label)
        body_label.setWordWrap(True)
        layout.addWidget(body_label)
        return container, layout

    def _build_getting_started(self) -> QWidget:
        container, layout = self._build_text_block(GETTING_API_KEY_KEY)
        layout.addLayout(self._build_link_buttons())
        return container

    def _build_link_buttons(self) -> QHBoxLayout:
        profile_column = self._build_labelled_link("Open profile", PROFILE_URL)
        docs_column = self._build_labelled_link("API docs", API_DOCS_URL)

        button_row = QHBoxLayout()
        button_row.setContentsMargins(0, 8, 0, 0)
        button_row.setSpacing(LINK_BUTTON_SPACING)
        button_row.addStretch(1)
        button_row.addWidget(profile_column, alignment=Qt.AlignmentFlag.AlignVCenter)
        button_row.addWidget(docs_column, alignment=Qt.AlignmentFlag.AlignVCenter)
        button_row.addStretch(1)
        return button_row

    def _build_labelled_link(self, caption: str, url: str) -> QWidget:
        button = TransparentToolButton(lucide_qicon(LucideIcon.EXTERNAL_LINK, TEXT_COLOR), self)
        button.setFixedSize(LINK_BUTTON_SIZE, LINK_BUTTON_SIZE)
        button.setIconSize(QSize(LINK_BUTTON_ICON_SIZE, LINK_BUTTON_ICON_SIZE))
        button.clicked.connect(lambda: webbrowser.open(url))

        caption_label = CaptionLabel(caption, self)
        apply_caption_font(caption_label)

        column_widget = QWidget(self)
        column = QVBoxLayout(column_widget)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(0)
        column.addWidget(button, alignment=Qt.AlignmentFlag.AlignHCenter)
        column.addWidget(caption_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        return column_widget
