from typing import Any

from cx_Freeze import Executable, setup
from cx_Freeze.command.bdist_msi import PyDialog
from cx_Freeze.command.bdist_msi import bdist_msi as _BdistMsi

from subsearch.data import __guid__

APP_NAME = "Subsearch"
ICON = "src/subsearch/gui/resources/assets/subsearch.ico"
_libs_to_exclude = [
    "concurrent",
    "lib2to3",
    "multiprocessing",
    "distutils",
    "tcl8",
    "test",
    "unittest",
    "xml",
    "xmlrpc",
    "asyncio",
    "chardet",
]


def _get_data_table() -> dict[str, Any]:
    script_component = f"_cx_executable0__Executable_script_src_{APP_NAME.lower()}___main__.py_"
    registry_path = rf"Software\Classes\*\shell\Subsearch"
    data = {
        "Registry": {
            (f"{APP_NAME}_key", -1, registry_path, None, None, script_component),
            (f"{APP_NAME}_regz_icon", -1, registry_path, "Icon", None, script_component),
            (f"{APP_NAME}_regz_appliesto", -1, registry_path, "AppliesTo", None, script_component),
            (f"{APP_NAME}_key_command", -1, rf"{registry_path}\command", None, "", script_component),
        },
    }
    return data


def get_executable() -> list[Executable]:
    executable = [
        Executable(
            "src/subsearch/__main__.py",
            base="Win32GUI",
            target_name=APP_NAME,
            icon=ICON,
            shortcut_name="Subsearch",
            shortcut_dir="ProgramMenuFolder",
        )
    ]
    return executable


def get_options() -> dict[str, Any]:
    data = _get_data_table()
    bdist_msi = {"upgrade_code": f"{__guid__}", "install_icon": ICON, "data": data}
    build_exe = {"excludes": [*_libs_to_exclude]}
    options = {"build_exe": build_exe, "bdist_msi": bdist_msi}
    return options


def main() -> None:
    executable = get_executable()
    options = get_options()
    # monkey_patch_exit_dialog()
    setup(options=options, executables=executable)


if __name__ == "__main__":
    main()
