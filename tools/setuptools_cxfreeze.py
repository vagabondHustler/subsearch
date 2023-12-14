import os
import sys

from cx_Freeze import Executable, setup
from cx_Freeze.command.bdist_msi import BdistMSI

from tools import monkey_patching
from subsearch.data import __guid__

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

APP_NAME = "Subsearch"
ICON = "src/subsearch/gui/resources/assets/subsearch.ico"
REGISTRY_PATH = rf"Software\Classes\*\shell\Subsearch"
MAIN_PATH = "src/subsearch/__main__.py"
GUID = __guid__


def add_extra_registry_keys():
    script_component = f"_cx_executable0__Executable_script_src_{APP_NAME.lower()}___main__.py_"
    key_subsearch = (f"{APP_NAME}_key", -1, REGISTRY_PATH, None, None, script_component)
    regz_icon = (f"{APP_NAME}_regz_icon", -1, REGISTRY_PATH, "Icon", None, script_component)
    regz_appliesto = (f"{APP_NAME}_regz_appliesto", -1, REGISTRY_PATH, "AppliesTo", None, script_component)
    key_command = (f"{APP_NAME}_key_command", -1, rf"{REGISTRY_PATH}\command", None, "", script_component)
    data = {"Registry": {key_subsearch, regz_icon, regz_appliesto, key_command}}
    return data


def get_executable():
    executable = [
        Executable(
            MAIN_PATH,
            base="Win32GUI",
            target_name=APP_NAME,
            icon=ICON,
            shortcut_name="Subsearch",
            shortcut_dir="ProgramMenuFolder",
        )
    ]
    return executable


def get_options():
    data = add_extra_registry_keys()
    bdist_msi = {"upgrade_code": f"{GUID}", "install_icon": ICON, "data": data}
    options = {"bdist_msi": bdist_msi}
    return options


def monkey_patch_cx_freeze():
    BdistMSI.add_config = monkey_patching.BdistMSI.add_config
    BdistMSI.add_exit_dialog = monkey_patching.BdistMSI.add_exit_dialog


def main():
    """
    Builds an executable and MSI installer using a monkey_patched version of cx_Freeze's BdistMSI class.

    """
    executable = get_executable()
    options = get_options()
    monkey_patch_cx_freeze()
    setup(options=options, executables=executable)


if __name__ == "main":
    main()
