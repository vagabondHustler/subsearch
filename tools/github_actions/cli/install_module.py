import importlib
import subprocess
from types import ModuleType


def _psutil() -> ModuleType:
    return _import_or_install("psutil", "psutil")


def _dotenv() -> ModuleType:
    return _import_or_install("python-dotenv", "dotenv")


def _install(lib) -> None:
    print(f"Installing {lib}...")
    subprocess.run(["pip", "install", lib])
    print(f"{lib} has been installed.")


def _import_or_install(lib, module_name) -> ModuleType:
    try:
        return importlib.import_module(module_name)
    except ImportError:
        _install(lib)
        return importlib.import_module(module_name)
