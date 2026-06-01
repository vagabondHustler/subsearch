import threading

import pystray
from PIL import Image

from subsearch import metaclasses
from subsearch.decorators import gui as gui_decorators
from subsearch.logging import log
from subsearch.runtime.constants import APP_PATHS, VERSION


class SystemTray(metaclass=metaclasses.Singleton):
    @gui_decorators.system_tray_conditions
    def __init__(self) -> None:
        title = f"Subsearch {VERSION}"
        icon = Image.open(APP_PATHS.gui_assets / "subsearch.ico")
        self.tray = pystray.Icon("Subsearch", icon=icon, title=title)
        self.thread_tray = threading.Thread(daemon=True, target=self._run_pystray)

    @gui_decorators.system_tray_conditions
    def display_toast(self, title: str, msg: str) -> None:
        self.tray.notify(msg, title)

    @gui_decorators.system_tray_conditions
    def start(self) -> None:
        log.stdout("Subsearch was added to the system tray", level="debug")
        self.thread_tray.start()

    @gui_decorators.system_tray_conditions
    def stop(self) -> None:
        self.tray.stop()
        self.thread_tray.join()
        log.stdout("Subsearch was removed from the system tray", level="debug")

    def _run_pystray(self) -> None:
        self.tray.run()
