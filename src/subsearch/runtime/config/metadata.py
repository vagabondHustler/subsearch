import platform
import socket
import sys

from subsearch.runtime.config.guid import __guid__
from subsearch.runtime.config.version import __version__
from subsearch.runtime.models import SystemInfo, WindowsRegistryPaths

COMPUTER_NAME: str = socket.gethostname()

APP_VERSION: str = str(__version__)

APP_GUID: str = str(__guid__)


def get_system_info() -> SystemInfo:
    if getattr(sys, "frozen", False):
        mode = "executable"
        python_version = ""
    else:
        python_version = platform.python_version()
        mode = "interpreter"
    platform_description = _describe_windows()
    return SystemInfo(platform_description, mode, python_version, __version__)


def _describe_windows() -> str:
    version = sys.getwindowsversion()
    # Windows 11 still reports major version 10; build >= 22000 is what distinguishes it
    release = "11" if version.build >= 22000 else "10"
    service_pack = version.service_pack or "SP0"
    return f"windows-{release}-{version.major}.{version.minor}.{version.build}-{service_pack}".lower()


def get_windows_registry_paths() -> WindowsRegistryPaths:
    return WindowsRegistryPaths(
        classes=r"Software\Classes",
        asterisk=r"Software\Classes\*",
        shell=r"Software\Classes\*\shell",
        subsearch=r"Software\Classes\*\shell\Subsearch",
        subsearch_command=r"Software\Classes\*\shell\Subsearch\command",
        long_paths=r"SYSTEM\CurrentControlSet\Control\FileSystem",
    )
