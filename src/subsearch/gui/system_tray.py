import threading

import pystray
from PIL import Image

from subsearch.data import __version__
from subsearch.data.constants import APP_PATHS

enable_system_tray: bool


def system_tray_conditions(func):
    def wrapper(*args, **kwargs):
        if enable_system_tray:
            return func(*args, **kwargs)
        else:
            ...

    return wrapper


class SystemTray:
    """
    A class representing a system tray instance.

    Attributes:
        tray (pystray.Icon): The system tray icon.
        thread_tray (threading.Thread): The thread for running the system tray.

    Methods:
        __init__(): Initializes the SystemTray class.
        start(): Starts the system tray instance.
        stop(): Stops the system tray instance.
    """

    @system_tray_conditions
    def __init__(self) -> None:
        title = f"Subsearch {__version__}"
        icon = Image.open(APP_PATHS.gui_assets / "subsearch.ico")
        self.tray = pystray.Icon("Subsearch", icon=icon, title=title)
        self.thread_tray = threading.Thread(daemon=True, target=self._run_pystray)

    @system_tray_conditions
    def display_toast(self, title: str, msg: str):
        self.tray.title
        self.tray.notify(msg, title)

    @system_tray_conditions
    def start(self) -> None:
        self.thread_tray.start()

    @system_tray_conditions
    def stop(self) -> None:
        self.tray.stop()
        self.thread_tray.join()

    def _run_pystray(self) -> None:
        self.tray.run()
