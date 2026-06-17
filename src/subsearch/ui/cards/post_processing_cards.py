from PySide6.QtCore import QEvent, QSize, Qt
from PySide6.QtGui import QEnterEvent, QMouseEvent
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QWidget,
)
from qfluentwidgets import (
    BodyLabel,
    CheckBox,
    TransparentToolButton,
)

from subsearch.runtime.config.defaults import ConfigKey
from subsearch.ui.cards.base import SettingsCard
from subsearch.ui.cards.descriptions import SETTING_DESCRIPTIONS, CardKey
from subsearch.ui.icons.lucide import LucideIcon, lucide_qicon
from subsearch.ui.services.shell_integration import ShellIntegrationService
from subsearch.ui.state.store import SettingsStore
from subsearch.ui.theme.metrics import CARD_CONTENT_INSET
from subsearch.ui.theme.typography import (
    TEXT_COLOR,
    apply_body_font,
)
from subsearch.ui.widgets.setting_rows import SwitchRow


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


class FileExtensionsCard(SettingsCard):
    def __init__(
        self, store: SettingsStore, shell_service: ShellIntegrationService, parent: QWidget | None = None
    ) -> None:
        super().__init__("File extensions", show_restore_button=False, parent=parent)
        self.store = store
        self.shell_service = shell_service
        store.subscribe(ConfigKey.SHELL_INTEGRATION_CONTEXT_MENU, self.set_enabled)
        self.add_header_help(SETTING_DESCRIPTIONS[ConfigKey.SHELL_INTEGRATION_FILE_EXTENSIONS].explanation)

        file_extensions = store.read(ConfigKey.SHELL_INTEGRATION_FILE_EXTENSIONS)
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
        self.set_enabled(bool(store.read(ConfigKey.SHELL_INTEGRATION_CONTEXT_MENU)))
        store.value_changed.connect(self._on_store_changed)

    def _on_store_changed(self, key: str, value: object) -> None:
        if key != ConfigKey.SHELL_INTEGRATION_FILE_EXTENSIONS:
            return
        if not isinstance(value, dict):
            return
        for extension, check_box in self.check_boxes.items():
            check_box.blockSignals(True)
            check_box.setChecked(bool(value.get(extension, False)))
            check_box.blockSignals(False)

    def _on_extension_toggled(self, extension: str, checked: bool) -> None:
        file_extensions = self.store.read(ConfigKey.SHELL_INTEGRATION_FILE_EXTENSIONS)
        file_extensions[extension] = checked
        self._persist_file_extensions(file_extensions)

    def _invert_selection(self) -> None:
        file_extensions = self.store.read(ConfigKey.SHELL_INTEGRATION_FILE_EXTENSIONS)
        for extension, check_box in self.check_boxes.items():
            inverted = not check_box.isChecked()
            check_box.blockSignals(True)
            check_box.setChecked(inverted)
            check_box.blockSignals(False)
            file_extensions[extension] = inverted
        self._persist_file_extensions(file_extensions)

    def _persist_file_extensions(self, file_extensions: dict) -> None:
        self.store.write(ConfigKey.SHELL_INTEGRATION_FILE_EXTENSIONS, file_extensions)
        self.shell_service.reconcile()

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
        self.add_header_help(SETTING_DESCRIPTIONS[CardKey.SHELL_INTEGRATION].explanation)

        self.context_menu = SwitchRow(ConfigKey.SHELL_INTEGRATION_CONTEXT_MENU, store)
        self.context_menu_icon = SwitchRow(ConfigKey.SHELL_INTEGRATION_CONTEXT_MENU_ICON, store)
        self.add_row(self.context_menu)
        self.add_row(self.context_menu_icon)
        self.context_menu.toggled.connect(self._on_context_menu_toggled)
        self.context_menu_icon.toggled.connect(self._on_context_menu_icon_toggled)
        self.context_menu_icon.set_enabled(self.context_menu.switch.isChecked())

    def _on_context_menu_toggled(self, enabled: bool) -> None:
        self.shell_service.reconcile()
        self.context_menu_icon.set_enabled(enabled)

    def _on_context_menu_icon_toggled(self) -> None:
        self.shell_service.reconcile()
