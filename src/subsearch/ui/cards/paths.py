from PySide6.QtWidgets import QVBoxLayout, QWidget
from qfluentwidgets import MessageBox

from subsearch.runtime.config import VIDEO_FILE
from subsearch.ui.cards.base import SettingsCard
from subsearch.ui.cards.descriptions import SETTING_DESCRIPTIONS
from subsearch.ui.state.store import SettingsStore
from subsearch.ui.theme.separators import make_fading_separator
from subsearch.ui.widgets.setting_rows import DirectoryPathRow, SwitchRow

DEFAULT_VIDEO_FILE_DIRECTORY = "."
DEFAULT_PATH_RESOLUTION = "relative"
DEFAULT_DIRECTORY = ""


class PathsCard(SettingsCard):
    def __init__(self, store: SettingsStore, parent: QWidget | None = None) -> None:
        super().__init__("Paths", store, parent=parent)
        self.store = store
        self.add_header_help(SETTING_DESCRIPTIONS["card.paths"].explanation)
        self.register_restore_defaults(
            [
                ("paths.download_directory", DEFAULT_DIRECTORY),
                ("paths.extraction_directory", DEFAULT_DIRECTORY),
                ("paths.video_file_directory", DEFAULT_VIDEO_FILE_DIRECTORY),
                ("paths.path_resolution", DEFAULT_PATH_RESOLUTION),
            ]
        )

        self.body_layout.addWidget(
            DirectoryPathRow(
                "paths.download_directory",
                store,
                placeholder_text="%TEMP%/tmp_subsearch",
                dialog_title="Select download directory",
                allow_empty=True,
            )
        )
        self.body_layout.addWidget(
            DirectoryPathRow(
                "paths.extraction_directory",
                store,
                placeholder_text="Downloads/subs",
                dialog_title="Select extraction directory",
                allow_empty=True,
            )
        )
        self._video_file_section = self._build_video_file_section(store)
        self.body_layout.addWidget(self._video_file_section)
        self._video_file_section.setEnabled(VIDEO_FILE.file_exists)

    def _build_video_file_section(self, store: SettingsStore) -> QWidget:
        container = QWidget(self)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.video_file_directory = DirectoryPathRow(
            "paths.video_file_directory",
            store,
            placeholder_text=".",
            dialog_title="Select video file directory",
            allow_empty=True,
        )
        self.video_file_directory.path_saved.connect(self._on_video_file_directory_saved)
        layout.addWidget(self.video_file_directory)

        create_missing_directory = SwitchRow("paths.create_missing_directory", store, container)
        layout.addWidget(create_missing_directory)
        self.register_restore_defaults([(create_missing_directory.config_key, create_missing_directory.default_value)])
        return container

    def _on_video_file_directory_saved(self, _path: str, path_resolution: str) -> None:
        self.store.write("paths.path_resolution", path_resolution)

    def commit_path_or_revert(self) -> bool:
        if not self._video_file_section.isEnabled():
            return True
        if self.video_file_directory.is_valid():
            self.video_file_directory.save_if_valid()
            return True
        return self._prompt_invalid_path_on_exit()

    def _prompt_invalid_path_on_exit(self) -> bool:
        confirmation = MessageBox(
            "Video file directory is not valid",
            f'The video file directory\n\n"{self.video_file_directory.text()}"\n\nis not valid. '
            f'Exit anyway and reset it to the default ("{DEFAULT_VIDEO_FILE_DIRECTORY}"), '
            "or stay and fix it?",
            self.window(),
        )
        confirmation.yesButton.setText("Reset and exit")
        confirmation.cancelButton.setText("Stay and fix")
        if not confirmation.exec():
            return False
        self.video_file_directory.set_path(DEFAULT_VIDEO_FILE_DIRECTORY)
        return True
