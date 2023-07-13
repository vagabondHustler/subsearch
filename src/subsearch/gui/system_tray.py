import threading
from typing import LiteralString

import pystray
from PIL import Image

from subsearch.data import __version__, app_paths
from subsearch.utils.state_machine import StateMachine, States


class SystemTray(StateMachine):
    """
    A class representing a system tray instance.

    Attributes:
        tray (pystray.Icon): The system tray icon.
        thread_tray (threading.Thread): The thread for running the system tray.

    Methods:
        __init__(): Initializes the SystemTray class.
        update_progress_state(): Updates the progress state of the system tray.
        lock_to_state(state: str): Locks the system tray to a specific state.
        prettified_tooltip(): Generates a prettified tooltip for the system tray.
        start(): Starts the system tray instance.
        stop(): Stops the system tray instance.
        _run_pystray(): Runs the system tray in a separate thread.
        _state_to_progressbar() -> int: Converts the current state to a progress bar value.
        _create_progress_bar(progress, width=15): Creates a progress bar string based on the given progress value.
    """

    def __init__(self) -> None:
        StateMachine.__init__(self)
        self.state_machine = StateMachine()
        title = self.prettified_tooltip()
        icon = Image.open(app_paths.gui_assets / "subsearch.ico")
        self.tray = pystray.Icon("Subsearch", icon=icon, title=title)
        self.thread_tray = threading.Thread(target=self._run_pystray)

    def update_progress_state(self) -> None:
        self._next_state()
        self.tray.title = self.prettified_tooltip()
        self.tray.update_menu()

    def lock_to_state(self, state: str) -> None:
        """
        Locks the system tray to a specific state, even if update_progress_state is called

        Args:
            state (str): "no_file", "gui", "exit"
        """
        states = {"no_file": States.NO_FILE.value, "gui": States.GUI.value, "exit": States.EXIT.value}
        self.set_state(states[state])
        self.tray.title = self.prettified_tooltip()
        self.tray.update_menu()

    def prettified_tooltip(self) -> str:
        pct = self._state_to_progressbar()
        status = str(self.state).split(".")[-1].capitalize().replace("_", " ")
        return f" {status}\n{pct}"

    def toast_message(self, msg: str, title: str | None = None):
        self.tray.notify(msg, title)

    def start(self) -> None:
        self.thread_tray.start()

    def stop(self) -> None:
        self.tray.stop()
        self.thread_tray.join()

    def _run_pystray(self) -> None:
        self.tray.run()

    def _state_to_progressbar(self) -> int:
        if self.state.name == States.EXIT.name:
            pct = 100
        elif self.state.name == States.UNKNOWN.name or self.state.name in self.locked_states:
            pct = 0
        else:
            state_values = [state.value for state in States if state.name not in self.locked_states]
            total_states = len(state_values)
            current_index = state_values.index(self.state.value)
            pct = int((current_index) / total_states * 100)

        return self._create_progress_bar(pct)

    def _create_progress_bar(self, progress, width=15) -> LiteralString:
        width_filled = int(progress / 100 * width)
        width_empty = width - width_filled
        bar_filled = "█" * width_filled
        bar_empty = "░" * width_empty
        bar = f"|{bar_filled}{bar_empty}|"
        return bar
