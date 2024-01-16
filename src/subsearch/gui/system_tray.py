import threading

import pystray
from PIL import Image

from subsearch.globals.constants import APP_PATHS, VERSION
from subsearch.globals import decorators
from subsearch.globals import metaclasses


class SystemTray(metaclass=metaclasses.Singleton):
    @decorators.system_tray_conditions
    def __init__(self) -> None:
        title = f"Subsearch {VERSION}"
        icon = Image.open(APP_PATHS.gui_assets / "subsearch.ico")
        self.tray = pystray.Icon("Subsearch", icon=icon, title=title)
        self.thread_tray = threading.Thread(daemon=True, target=self._run_pystray)

    @decorators.system_tray_conditions
    def display_toast(self, title: str, msg: str) -> None:
        self.tray.title
        self.tray.notify(msg, title)

    @decorators.system_tray_conditions
    def start(self) -> None:
        self.thread_tray.start()

    @decorators.system_tray_conditions
    def stop(self) -> None:
        self.tray.stop()
        self.thread_tray.join()

    def _run_pystray(self) -> None:
        self.tray.run()
