from PySide6.QtWidgets import QVBoxLayout, QWidget
from qfluentwidgets import MessageBox

from subsearch.ui.cards.base import SettingsCard
from subsearch.ui.cards.descriptions import SETTING_DESCRIPTIONS
from subsearch.ui.state.store import SettingsStore
from subsearch.ui.theme.separators import make_fading_separator
from subsearch.ui.widgets.setting_rows import (
    FolderPathRow,
    SwitchRow,
    make_switches_mutually_exclusive,
)

DEFAULT_TARGET_PATH = "."
DEFAULT_PATH_RESOLUTION = "relative"
DEFAULT_WORKING_DIRECTORY = ""
WORKING_DIRECTORY_PLACEHOLDER = "Let Subsearch decide (Downloads\\subs)"
DESTINATION_PATH_EXAMPLES = (
    "Where moved subtitles are placed.\n\n"
    "Relative , taken from the video's own folder:\n"
    "    subs\n"
    "    ..\\Subtitles\n\n"
    "Absolute , a fixed path on disk:\n"
    "    C:\\Users\\You\\Subtitles\n"
    "    D:\\Media\\Subs"
)


class SubtitleHandlingCard(SettingsCard):
    def __init__(self, store: SettingsStore, parent: QWidget | None = None) -> None:
        super().__init__("Subtitle handling", store, parent=parent)
        self.store = store
        self.add_header_help(SETTING_DESCRIPTIONS["card.subtitle_handling"].explanation)
        self.register_restore_defaults(
            [
                ("post_processing.target_path", DEFAULT_TARGET_PATH),
                ("post_processing.path_resolution", DEFAULT_PATH_RESOLUTION),
                ("download_manager.working_directory", DEFAULT_WORKING_DIRECTORY),
            ]
        )

        self._automatic_handling = self._build_automatic_handling()
        self.body_layout.addWidget(self._automatic_handling)

        self._build_destination()

        self.add_row(SwitchRow("download_manager.manually_handle_post_processing", store))

        self.body_layout.addWidget(make_fading_separator(opacity=0.6, width_fraction=0.75, vertical_margin=8))

        self._working_directory_row = FolderPathRow(
            "download_manager.working_directory",
            store,
            placeholder_text=WORKING_DIRECTORY_PLACEHOLDER,
            dialog_title="Select working folder",
            allow_empty=True,
        )
        self.body_layout.addWidget(self._working_directory_row)

        self._update_destination_enabled()
        self._apply_manual_handle_state(bool(store.read("download_manager.manually_handle_post_processing")))
        store.value_changed.connect(self._on_store_changed)

    def _build_automatic_handling(self) -> QWidget:
        container = QWidget(self)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        rename = SwitchRow("post_processing.rename", self.store)
        self.move_best = SwitchRow("post_processing.move_best", self.store)
        self.move_all = SwitchRow("post_processing.move_all", self.store)
        layout.addWidget(rename)
        layout.addWidget(self.move_best)
        layout.addWidget(self.move_all)
        for row in (rename, self.move_best, self.move_all):
            self.register_restore_defaults([(row.config_key, row.default_value)])
        make_switches_mutually_exclusive(self.move_best, self.move_all)
        self.move_best.toggled.connect(self._update_destination_enabled)
        self.move_all.toggled.connect(self._update_destination_enabled)
        return container

    def _build_destination(self) -> None:
        self.destination = QWidget(self)
        destination_layout = QVBoxLayout(self.destination)
        destination_layout.setContentsMargins(0, 0, 0, 0)

        self.destination_path = FolderPathRow("post_processing.target_path", self.store, DESTINATION_PATH_EXAMPLES)
        self.destination_path.path_saved.connect(self._on_destination_path_saved)
        destination_layout.addWidget(self.destination_path)

        create_missing_folder = SwitchRow("post_processing.create_missing_folder", self.store, self)
        destination_layout.addWidget(create_missing_folder)
        self.register_restore_defaults([(create_missing_folder.config_key, create_missing_folder.default_value)])
        self.body_layout.addWidget(self.destination)

    def _on_store_changed(self, key: str, value: object) -> None:
        if key == "download_manager.manually_handle_post_processing":
            self._apply_manual_handle_state(bool(value))

    def _apply_manual_handle_state(self, manual_enabled: bool) -> None:
        self._automatic_handling.setEnabled(not manual_enabled)
        if manual_enabled:
            self.destination.setEnabled(True)
        else:
            self._update_destination_enabled()

    def _update_destination_enabled(self, _checked: bool = False) -> None:
        if self.store.read("download_manager.manually_handle_post_processing"):
            return
        moving_enabled = self.move_best.switch.isChecked() or self.move_all.switch.isChecked()
        self.destination.setEnabled(moving_enabled)

    def _on_destination_path_saved(self, _path: str, path_resolution: str) -> None:
        self.store.write("post_processing.path_resolution", path_resolution)

    def commit_path_or_revert(self) -> bool:
        if self.destination_path.is_valid():
            self.destination_path.save_if_valid()
            return True
        return self._prompt_invalid_path_on_exit()

    def _prompt_invalid_path_on_exit(self) -> bool:
        confirmation = MessageBox(
            "Destination folder is not valid",
            f'The destination folder\n\n"{self.destination_path.text()}"\n\nis not valid. '
            f'Exit anyway and reset it to the default ("{DEFAULT_TARGET_PATH}"), '
            "or stay and fix it?",
            self.window(),
        )
        confirmation.yesButton.setText("Reset and exit")
        confirmation.cancelButton.setText("Stay and fix")
        if not confirmation.exec():
            return False
        self.destination_path.set_path(DEFAULT_TARGET_PATH)
        return True
