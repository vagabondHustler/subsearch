import tkinter as tk
from tkinter import ttk
from typing import Literal

from subsearch.globals.constants import (
    APP_PATHS,
    CONFIG_CONFLICT_MAP,
    FILE_PATHS,
    DISABLE_STATE_MAP,
    REGISTRY_OPTIONS_MAP,
)
from subsearch.gui.resources import config as cfg
from subsearch.utils import io_toml, io_winreg
from subsearch.globals import log

Anchor = Literal["nw", "n", "ne", "w", "center", "e", "sw", "s", "se"]


class ConfigManager:
    @staticmethod
    def get(key: str) -> bool:
        return io_toml.load_toml_value(FILE_PATHS.config, key)

    @staticmethod
    def set(key: str, value: bool) -> None:
        io_toml.update_toml_key(FILE_PATHS.config, key, value)

    @staticmethod
    def update_checkbutton(key: str, value: bool = False) -> None:
        if key in CheckbuttonWidgets.widgets:
            CheckbuttonWidgets.widgets[key][1].set(value)


class RegistryManager:
    @staticmethod
    def sync_context_menu() -> None:
        if ConfigManager.get("gui.context_menu"):
            io_winreg.add_context_menu()
        else:
            io_winreg.del_context_menu()


class ConflictManager:
    @staticmethod
    def has_conflict(key: str, value: bool) -> bool:
        return value and key in CONFIG_CONFLICT_MAP

    @staticmethod
    def resolve(key: str) -> None:
        for conflicting_key in CONFIG_CONFLICT_MAP.get(key, []):
            ConfigManager.update_checkbutton(conflicting_key, False)
            ConfigManager.set(conflicting_key, False)

    @staticmethod
    def update_dependent_widgets(key: str) -> None:
        if key in DISABLE_STATE_MAP:
            is_enabled = ConfigManager.get(key)
            ConflictManager._handle_dependent_key(key, is_enabled)

    def _handle_dependent_key(key, is_enabled: bool) -> None:
        dependent_keys = DISABLE_STATE_MAP[key]
        for _key in dependent_keys:
            if _key in CheckbuttonWidgets.widgets:
                ConflictManager._update_checkbutton_state(is_enabled, _key)

    def _update_checkbutton_state(is_enabled: bool, dependent_key: str) -> None:
        checkbutton, _ = CheckbuttonWidgets.widgets[dependent_key]
        checkbutton["state"] = "normal" if is_enabled else "disabled"


class CheckbuttonWidgets:
    widgets: dict[str, tuple[ttk.Checkbutton, tk.BooleanVar]] = {}

    def __init__(self, parent: ttk.Labelframe, config_keys: dict[str, str], columns: int = 1) -> None:
        self.parent = parent
        self.config_keys = config_keys
        self.columns = columns
        self.current_frame = None

    def get_widgets(self) -> dict[str, tuple[ttk.Checkbutton, tk.BooleanVar]]:
        return CheckbuttonWidgets.widgets

    def create(self, anchor: Anchor, padx: int, pady: int, ipadx: int) -> None:
        for index, (key, label) in enumerate(self.config_keys.items()):
            if index % self.columns == 0:
                self.current_frame = ttk.Frame(self.parent)
                self.current_frame.pack(side=tk.LEFT, anchor=anchor, expand=True)

            var = tk.BooleanVar(value=ConfigManager.get(key))
            checkbutton = ttk.Checkbutton(self.current_frame, text=label, variable=var, onvalue=True, offvalue=False)
            checkbutton.config(command=lambda k=key: self._on_toggle(k))
            checkbutton.pack(anchor=anchor, padx=padx, pady=pady, ipadx=ipadx)

            CheckbuttonWidgets.widgets[key] = (checkbutton, var)

        self.parent.after_idle(self._initialize_widget_states)

    def _on_toggle(self, key: str) -> None:
        value = CheckbuttonWidgets.widgets[key][1].get()
        log.stdout(f"Updated {key} to {value}")
        ConfigManager.set(key, value)

        if ConflictManager.has_conflict(key, value):
            ConflictManager.resolve(key)
            log.stdout(f"Resolved exclusive option(s)")

        ConflictManager.update_dependent_widgets(key)
        if key in REGISTRY_OPTIONS_MAP:
            log.stdout(f"Windows registry updated")
            RegistryManager.sync_context_menu()

    def _initialize_widget_states(self) -> None:
        ConflictManager.update_dependent_widgets("gui.context_menu")


class WindowPosition(tk.Frame):
    def __init__(self, parent) -> None:
        tk.Frame.__init__(self, parent)

    def set(self, **kwargs) -> str:
        w = kwargs.get("w", cfg.size.width)
        h = kwargs.get("h", cfg.size.height)
        ws_value_offset = kwargs.get("ws_value_offset", 0)
        hs_value_offset = kwargs.get("hs_value_offset", 0)
        ws = self.winfo_screenwidth() + ws_value_offset
        hs = self.winfo_screenheight() + hs_value_offset
        x = int((ws / 2) - (w / 2))
        y = int((hs / 2) - (h / 2))
        value = f"{w}x{h}+{x}+{y}"
        return value


class ToolTip(tk.Toplevel):
    def __init__(self, parent, widget, *text_strings, **kwargs) -> None:
        super().__init__(parent)
        self.parent = parent
        self.widget = widget
        self.text = text_strings
        self.background = kwargs.get("bg", cfg.color.light_black)
        self.foreground = kwargs.get("fg", cfg.color.default_fg)

        self._setup_window()

    def _setup_window(self) -> None:
        """Initial tooltip window configuration."""
        self.configure(background=self.background)
        self.overrideredirect(True)  # remove the title bar

    def _create_content(self) -> tuple[tk.Frame, tk.Label]:
        """Create and return the tooltip frame and label."""
        lines = "\n".join(self.text)
        frame = tk.Frame(self, background=self.background)
        label = tk.Label(
            frame,
            text=lines,
            background=self.background,
            foreground=self.foreground,
            justify="left",
        )
        return frame, label

    def _position_window(self, frame: tk.Frame, label: tk.Label) -> None:
        """Calculate and set the position and size of the tooltip window."""
        label.update_idletasks()
        x, y = label.winfo_reqwidth(), label.winfo_reqheight()

        frame.configure(width=x + 1, height=y + 1)
        frame.place(x=1, y=1, anchor="nw")
        label.place(x=0, y=0, anchor="nw")

        widget_posx = self.widget.winfo_rootx()
        widget_width = self.widget.winfo_reqwidth()
        widget_center = widget_posx + round(widget_width / 2)

        frame.update_idletasks()
        frame_width = frame.winfo_reqwidth()
        frame_center = round(frame_width / 2)

        root_x = widget_center - frame_center
        root_y = self.widget.winfo_rooty() - self.widget.winfo_height() - 4

        self.geometry(f"{x + 2}x{y + 2}+{root_x}+{root_y}")

    def show(self) -> None:
        """Display the tooltip."""
        frame, label = self._create_content()
        self._position_window(frame, label)

    def hide(self) -> None:
        """Hide (destroy) the tooltip."""
        self.destroy()


def configure_root(root) -> None:
    if io_toml.load_toml_value(FILE_PATHS.config, "gui.context_menu"):
        io_winreg.add_context_menu()
    root.configure(background=cfg.color.default_bg)
    root.iconbitmap(APP_PATHS.gui_assets / "subsearch.ico")
    root.geometry(WindowPosition.set(root))  # type: ignore
    root.resizable(False, False)
