from cx_Freeze import Executable, setup
from cx_Freeze.command.bdist_msi import BdistMSI, PyDialog

from subsearch.data import __guid__

APP_NAME = "Subsearch"
ICON = "src/subsearch/gui/resources/assets/subsearch.ico"


class MonekyPatchBdistMSI:
    @staticmethod
    def add_exit_dialog(cls):
        dialog = PyDialog(
            cls.db,
            "ExitDialog",
            cls.x,
            cls.y,
            cls.width,
            cls.height,
            cls.modal,
            cls.title,
            "Finish",
            "Finish",
            "Finish",
        )
        dialog.title("Completing the [ProductName] installer")
        dialog.text(
            "Description1",
            15,
            70,
            355,
            180,
            0x30003,
            "It's recommended to launch [ProductName] to ensure proper initialization.\n"
            "Can be done at a later point in time.",
        )
        launch_app = dialog.pushbutton(
            "Launch App", 25, 130, 320, 30, 3, "Launch [ProductName] and exit installer", None
        )
        launch_app.event("DoAction", "LAUNCH_APP", 'LAUNCHAPP="1"', "0")
        launch_app.event("EndDialog", "Return")
        dialog.backbutton("< Back", "Finish", active=False)
        dialog.cancelbutton("Cancel", "Back", active=False)
        dialog.text("Description", 15, 235, 320, 20, 0x30003, "Or click the Finish button exit the installer.")
        button = dialog.nextbutton("Finish", "Cancel", name="Finish")
        # button.event("SetProperty", "VSDCA_Launch", "LAUNCHAPP", "1")
        # button.event("DoAction", "VSDCA_Launch", 'LAUNCHAPP="1"', '0')
        button.event("EndDialog", "Return")


def _get_data():
    script_component = f"_cx_executable0__Executable_script_src_{APP_NAME.lower()}___main__.py_"
    registry_path = rf"Software\Classes\*\shell\Subsearch"
    data = {
        "Registry": {
            (f"{APP_NAME}_key", -1, registry_path, None, None, script_component),
            (f"{APP_NAME}_regz_icon", -1, registry_path, "Icon", None, script_component),
            (f"{APP_NAME}_regz_appliesto", -1, registry_path, "AppliesTo", None, script_component),
            (f"{APP_NAME}_key_command", -1, rf"{registry_path}\command", None, "", script_component),
        },
        "Property": {("LAUNCHAPP", 1)},
        "CustomAction": {("LAUNCH_APP", 210, "Subsearch.exe", "")},
    }
    return data


def get_executable():
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


def get_options():
    data = _get_data()
    bdist_msi = {"upgrade_code": f"{__guid__}", "install_icon": ICON, "data": data}
    options = {"bdist_msi": bdist_msi}
    return options


def monkey_patch_exit_dialog():
    BdistMSI.add_exit_dialog = MonekyPatchBdistMSI.add_exit_dialog


def main():
    executable = get_executable()
    options = get_options()
    monkey_patch_exit_dialog()
    setup(options=options, executables=executable)


if __name__ == "__main__":
    main()