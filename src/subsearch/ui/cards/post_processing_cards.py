from pathlib import Path

from PySide6.QtCore import QEvent, QSize, Qt
from PySide6.QtGui import QEnterEvent, QMouseEvent
from PySide6.QtWidgets import (
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import (
    BodyLabel,
    CheckBox,
    LineEdit,
    MessageBox,
    TransparentToolButton,
)

from subsearch.parsing import release_parser
from subsearch.ui.cards.base import SettingsCard, build_section_header
from subsearch.ui.cards.descriptions import SETTING_DESCRIPTIONS
from subsearch.ui.icons.lucide import LucideIcon, lucide_qicon
from subsearch.ui.services.shell_integration import ShellIntegrationService
from subsearch.ui.state.store import SettingsStore
from subsearch.ui.theme.metrics import CARD_CONTENT_INSET, ROW_INSET
from subsearch.ui.theme.typography import TEXT_COLOR, apply_body_font
from subsearch.ui.widgets.icon_caption_button import CaptionedToolButton
from subsearch.ui.widgets.setting_rows import (
    HelpButton,
    SwitchRow,
    make_switches_mutually_exclusive,
)


class _ButtonProxyLabel(BodyLabel):
    def __init__(self, text: str, button: TransparentToolButton, parent: QWidget | None = None) -> None:  # type: ignore[override]
        super().__init__(parent)
        self.setText(text)
        self._button = button

    def enterEvent(self, event: QEnterEvent) -> None:
        self._button.setAttribute(Qt.WidgetAttribute.WA_UnderMouse, True)
        self._button.update()
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        self._button.setAttribute(Qt.WidgetAttribute.WA_UnderMouse, False)
        self._button.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self._button.animateClick()


EXTENSION_GRID_ROWS = 3

DEFAULT_TARGET_PATH = "."
DEFAULT_PATH_RESOLUTION = "relative"
DESTINATION_PATH_EXAMPLES = (
    "Where moved subtitles are placed.\n\n"
    "Relative , taken from the video's own folder:\n"
    "    subs\n"
    "    ..\\Subtitles\n\n"
    "Absolute , a fixed path on disk:\n"
    "    C:\\Users\\You\\Subtitles\n"
    "    D:\\Media\\Subs"
)


class PostProcessingCard(SettingsCard):
    def __init__(self, store: SettingsStore, parent: QWidget | None = None) -> None:
        super().__init__("Subtitle post-processing", store, parent=parent)
        self.store = store
        self.add_header_help(SETTING_DESCRIPTIONS["card.post_processing"].explanation)
        self.register_restore_defaults([
            ("post_processing.target_path", DEFAULT_TARGET_PATH),
            ("post_processing.path_resolution", DEFAULT_PATH_RESOLUTION),
        ])
        self.add_row(SwitchRow("post_processing.rename", store))
        self.move_best = SwitchRow("post_processing.move_best", store)
        self.move_all = SwitchRow("post_processing.move_all", store)
        self.add_row(self.move_best)
        self.add_row(self.move_all)
        make_switches_mutually_exclusive(self.move_best, self.move_all)
        self.move_best.toggled.connect(self._update_destination_enabled)
        self.move_all.toggled.connect(self._update_destination_enabled)

        self._build_destination()
        self._update_destination_enabled()

    def _update_destination_enabled(self, _checked: bool = False) -> None:
        moving_enabled = self.move_best.switch.isChecked() or self.move_all.switch.isChecked()
        self.destination.setEnabled(moving_enabled)

    def _build_destination(self) -> None:
        self.destination = QWidget(self)
        destination_layout = QVBoxLayout(self.destination)
        destination_layout.setContentsMargins(0, 0, 0, 0)
        destination_layout.addLayout(build_section_header("post_processing.target_path", self))

        self.path_edit = LineEdit(self)
        self.path_edit.setText(str(self.store.read("post_processing.target_path")))
        self.path_edit.setClearButtonEnabled(True)
        apply_body_font(self.path_edit)
        self.path_edit.textChanged.connect(self._on_path_text_changed)
        self.path_edit.editingFinished.connect(self._save_path_if_valid)
        help_button = HelpButton(DESTINATION_PATH_EXAMPLES, self)
        path_row = QHBoxLayout()
        path_row.setContentsMargins(ROW_INSET, 0, ROW_INSET, 10)
        path_row.addWidget(self.path_edit, stretch=1)
        path_row.addWidget(self._build_browse_button())
        path_row.addWidget(help_button)
        destination_layout.addLayout(path_row)

        create_missing_folder = SwitchRow("post_processing.create_missing_folder", self.store, self)
        destination_layout.addWidget(create_missing_folder)
        self.register_restore_defaults([(create_missing_folder.config_key, create_missing_folder.default_value)])
        self.body_layout.addWidget(self.destination)

    def _build_browse_button(self) -> QWidget:
        browse_button = CaptionedToolButton(
            "Browse", icon=lucide_qicon(LucideIcon.FOLDER_OPEN, TEXT_COLOR), parent=self
        )
        browse_button.clicked.connect(self._browse_for_folder)
        return browse_button

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

    def _apply_path_error_style(self, is_error: bool) -> None:
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
        self._apply_path_error_style(False)
        self.store.write("post_processing.target_path", target_path)
        self.store.write("post_processing.path_resolution", path_resolution)

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
        self.store.write("post_processing.target_path", DEFAULT_TARGET_PATH)
        self.store.write("post_processing.path_resolution", DEFAULT_PATH_RESOLUTION)
        return True

    def _on_path_text_changed(self, target_path: str) -> None:
        path_resolution = release_parser.detect_path_resolution(target_path)
        self._apply_path_error_style(not release_parser.valid_path(target_path, path_resolution))


class FileExtensionsCard(SettingsCard):
    def __init__(
        self, store: SettingsStore, shell_service: ShellIntegrationService, parent: QWidget | None = None
    ) -> None:
        super().__init__("File extensions", show_restore_button=False, parent=parent)
        self.store = store
        self.shell_service = shell_service
        store.subscribe("shell_integration.context_menu", self.set_enabled)
        self.add_header_help(SETTING_DESCRIPTIONS["shell_integration.file_extensions"].explanation)

        file_extensions = store.read("shell_integration.file_extensions")
        self.check_boxes: dict[str, CheckBox] = {}
        grid = QGridLayout()
        grid.setContentsMargins(CARD_CONTENT_INSET, 0, CARD_CONTENT_INSET, 10)
        grid.setHorizontalSpacing(24)
        grid.setVerticalSpacing(12)
        column_count = -(-len(file_extensions) // EXTENSION_GRID_ROWS)
        for column in range(column_count):
            grid.setColumnStretch(column, 1)
        last_row = 0
        last_column = 0
        for index, (extension, enabled) in enumerate(file_extensions.items()):
            row = index % EXTENSION_GRID_ROWS
            column = index // EXTENSION_GRID_ROWS
            check_box = CheckBox(extension, self)
            apply_body_font(check_box)
            check_box.setChecked(bool(enabled))
            check_box.toggled.connect(lambda checked, ext=extension: self._on_extension_toggled(ext, checked))
            grid.addWidget(check_box, row, column, alignment=Qt.AlignmentFlag.AlignLeft)
            self.check_boxes[extension] = check_box
            last_row = row
            last_column = column

        self.invert_button = TransparentToolButton(lucide_qicon(LucideIcon.ARROW_LEFT_RIGHT, TEXT_COLOR), self)
        self.invert_button.setFixedSize(22, 22)
        self.invert_button.setIconSize(QSize(16, 16))
        self.invert_button.clicked.connect(self._invert_selection)

        self.invert_label = _ButtonProxyLabel("Invert selection", self.invert_button, self)
        apply_body_font(self.invert_label)
        self.invert_label.setCursor(self.invert_button.cursor())

        invert_row = QHBoxLayout()
        invert_row.setContentsMargins(0, 0, 0, 0)
        invert_row.setSpacing(6)
        invert_row.addWidget(self.invert_button)
        invert_row.addWidget(self.invert_label)

        invert_container = QWidget(self)
        invert_container.setLayout(invert_row)

        next_row = last_row + 1
        next_column = last_column
        if next_row >= EXTENSION_GRID_ROWS:
            next_row = 0
            next_column = last_column + 1
        grid.addWidget(invert_container, next_row, next_column, alignment=Qt.AlignmentFlag.AlignLeft)

        self.body_layout.addLayout(grid)
        self.set_enabled(bool(store.read("shell_integration.context_menu")))

    def _on_extension_toggled(self, extension: str, checked: bool) -> None:
        file_extensions = self.store.read("shell_integration.file_extensions")
        file_extensions[extension] = checked
        self._persist_file_extensions(file_extensions)

    def _invert_selection(self) -> None:
        file_extensions = self.store.read("shell_integration.file_extensions")
        for extension, check_box in self.check_boxes.items():
            inverted = not check_box.isChecked()
            check_box.blockSignals(True)
            check_box.setChecked(inverted)
            check_box.blockSignals(False)
            file_extensions[extension] = inverted
        self._persist_file_extensions(file_extensions)

    def _persist_file_extensions(self, file_extensions: dict) -> None:
        self.store.write("shell_integration.file_extensions", file_extensions)
        if self.store.read("shell_integration.context_menu"):
            self.shell_service.refresh_registry_value("appliesto")

    def set_enabled(self, enabled: bool) -> None:
        for check_box in self.check_boxes.values():
            check_box.setEnabled(enabled)
        self.invert_button.setEnabled(enabled)
        self.invert_label.setEnabled(enabled)


class ShellIntegrationCard(SettingsCard):
    def __init__(
        self,
        store: SettingsStore,
        shell_service: ShellIntegrationService,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__("Shell integration", store, parent=parent)
        self.store = store
        self.shell_service = shell_service
        self.add_header_help(SETTING_DESCRIPTIONS["card.shell_integration"].explanation)

        self.context_menu = SwitchRow("shell_integration.context_menu", store)
        self.context_menu_icon = SwitchRow("shell_integration.context_menu_icon", store)
        self.add_row(self.context_menu)
        self.add_row(self.context_menu_icon)
        self.context_menu.toggled.connect(self._on_context_menu_toggled)
        self.context_menu_icon.toggled.connect(self._on_context_menu_icon_toggled)
        self.context_menu_icon.set_enabled(self.context_menu.switch.isChecked())

    def _on_context_menu_toggled(self, enabled: bool) -> None:
        self.shell_service.set_context_menu_enabled(enabled)
        self.context_menu_icon.set_enabled(enabled)

    def _on_context_menu_icon_toggled(self) -> None:
        if self.store.read("shell_integration.context_menu"):
            self.shell_service.refresh_registry_value("icon")
