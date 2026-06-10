from PySide6.QtCore import Signal

from subsearch.io import app_updater
from subsearch.ui.state.tasks import Worker


class UpdateCheckWorker(Worker):
    def execute(self) -> app_updater.UpdateAvailability:
        return app_updater.check_for_update()


class UpdateInstallWorker(Worker):
    progress = Signal(float)

    def __init__(self, latest_version: str) -> None:
        super().__init__()
        self.latest_version = latest_version

    def execute(self) -> str:
        msi_package_path = app_updater.download_installer(self.latest_version, self.progress.emit)
        return str(msi_package_path)
