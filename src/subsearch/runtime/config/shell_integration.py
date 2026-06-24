import sys
from collections.abc import Mapping
from pathlib import Path

from subsearch.io import windows_registry
from subsearch.runtime.config import APP_PATHS, DEVICE_INFO, REGISTRY_PATHS
from subsearch.runtime.config import session as config_session
from subsearch.runtime.config.defaults import ConfigKey
from subsearch.runtime.recorder import LogLevel, capture

VALUE_LOCATIONS = {
    "subsearch": (REGISTRY_PATHS.subsearch, ""),
    "icon": (REGISTRY_PATHS.subsearch, "Icon"),
    "appliesto": (REGISTRY_PATHS.subsearch, "AppliesTo"),
    "command": (REGISTRY_PATHS.subsearch_command, ""),
}


class PythonExecutable:
    def __init__(self, show_terminal: bool) -> None:
        python_dir = Path(sys.executable).parent
        self.path = python_dir / ("python.exe" if show_terminal else "pythonw.exe")


class RegistryLaunchCommand:
    def __init__(self) -> None:
        show_terminal = config_session.read_config_value(ConfigKey.APPLICATION_SHOW_TERMINAL)
        self._mode = DEVICE_INFO.mode
        self._python_executable = PythonExecutable(show_terminal)

    def _executable_mode_command(self) -> str:
        return f'"{sys.argv[0]}" "%1"'

    def _interpreter_mode_command(self) -> str:
        console_title = "import ctypes; ctypes.windll.kernel32.SetConsoleTitleW('subsearch');"
        working_directory = f"import os; os.chdir(r'{APP_PATHS.home}');"
        import_subsearch = "import subsearch; subsearch.main()"
        return f'{self._python_executable.path} -c "{console_title} {working_directory} {import_subsearch}" "%1"'

    def build(self) -> str:
        if self._mode == "executable":
            return self._executable_mode_command()
        return self._interpreter_mode_command()


def get_command_value() -> str:
    return RegistryLaunchCommand().build()


def get_icon_value() -> str:
    show_icon: str = config_session.read_config_value(ConfigKey.SHELL_INTEGRATION_CONTEXT_MENU_ICON)
    if show_icon:
        return str(APP_PATHS.ui_assets / "subsearch.ico")
    return ""


def get_appliesto_value() -> str:
    file_extensions = config_session.read_config_value(ConfigKey.SHELL_INTEGRATION_FILE_EXTENSIONS)
    enabled_extensions = [f'".{ext}"' for ext, enabled in file_extensions.items() if enabled]
    return " OR ".join(enabled_extensions)


def desired_registry_values() -> dict[str, str]:
    return {
        "subsearch": "Subsearch",
        "icon": get_icon_value(),
        "appliesto": get_appliesto_value(),
        "command": get_command_value(),
    }


def changed_value_names(desired: Mapping[str, str], current: Mapping[str, str | None]) -> list[str]:
    return [name for name, value in desired.items() if current.get(name) != value]


def context_menu_enabled() -> bool:
    enabled: bool = config_session.read_config_value(ConfigKey.SHELL_INTEGRATION_CONTEXT_MENU)
    return enabled


def current_registry_values() -> dict[str, str | None]:
    return {
        name: windows_registry.read_registry_value(sub_key, value_name)
        for name, (sub_key, value_name) in VALUE_LOCATIONS.items()
    }


def reconcile_shell_integration() -> None:
    if not context_menu_enabled():
        if windows_registry.context_menu_key_exists():
            windows_registry.del_context_menu()
        else:
            capture("Registry matches config: context menu absent", level=LogLevel.DEBUG)
        return
    desired = desired_registry_values()
    stale_names = changed_value_names(desired, current_registry_values())
    if not stale_names:
        capture("Registry matches config: context menu up to date", level=LogLevel.DEBUG)
        return
    windows_registry.create_context_menu_keys()
    for name in stale_names:
        sub_key, value_name = VALUE_LOCATIONS[name]
        windows_registry.write_registry_value(sub_key, value_name, desired[name])
        capture(f"Registry updated: {name}")
