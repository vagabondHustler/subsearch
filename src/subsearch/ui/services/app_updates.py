from pathlib import Path

from PySide6.QtCore import Signal

from subsearch.io import app_updater
from subsearch.parsing import release_updates
from subsearch.parsing.release_updates import UpdateAvailability
from subsearch.ui.state.tasks import Worker


def launch_installer(msi_package_path: str) -> None:
    app_updater.run_installer(Path(msi_package_path))


class UpdateCheckWorker(Worker):
    def execute(self) -> UpdateAvailability:
        return release_updates.check_for_update()


class UpdateInstallWorker(Worker):
    progress = Signal(float)

    def __init__(self, latest_version: str) -> None:
        super().__init__()
        self.latest_version = latest_version

    def execute(self) -> str:
        msi_package_path = app_updater.download_installer(self.latest_version, self.progress.emit)
        return str(msi_package_path)
