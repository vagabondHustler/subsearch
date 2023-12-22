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
            "Run [ProductName] once to ensure proper initialization.\n"
            "This can be done at a later point in time.",
        )
        group = dialog.radiogroup(
            "RunRadioGroup",
            15,
            108,
            330,
            60,
            3,
            "RunSubsearch_Action",
            "",
            None,
        )
        group.add("Run", 0, 18, 300, 17, "Run [ProductName]")
        group.add("DoNothing", 0, 36, 300, 17, "Do nothing")

        dialog.backbutton("< Back", "Finish", active=False)
        dialog.cancelbutton("Cancel", "Back", active=False)
        dialog.text(
            "Description",
            15,
            235,
            320,
            20,
            0x30003,
            "Click the Finish button to exit the installer [RunSubsearch_Action].",
        )

        button = dialog.nextbutton("Finish", "Cancel", name="Finish")
        button.event("[RunApp]", "INSTALL", 'RunSubsearch_Action="Run"', 1)
        button.event("[DoNothing]", "INSTALL", 'RunSubsearch_Action="DoNothing"', 2)
        button.event("DoAction", "RunApp", 'RunSubsearch_Action="Run"', 3)
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
        "Property": {("RunSubsearch_Action", "DoNothing")},
        "CustomAction": {("RunApp", 210, "Subsearch.exe", "")},
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
