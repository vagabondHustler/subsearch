import msilib

from cx_Freeze.command._bdist_msi import bdist_msi as _bdist_msi
from cx_Freeze.command._pydialog import PyDialog


class BdistMSI(_bdist_msi):
    def add_config(self):
        if self.add_to_path:
            path = "Path"
            if self.all_users:
                path = "=-*" + path
            msilib.add_data(
                self.db,
                "Environment",
                [("E_PATH", path, r"[~];[TARGETDIR]", "TARGETDIR")],
            )
        if self.directories:
            msilib.add_data(self.db, "Directory", self.directories)
        if self.environment_variables:
            msilib.add_data(self.db, "Environment", self.environment_variables)
        # This is needed in case the AlwaysInstallElevated policy is set.
        # Otherwise installation will not end up in TARGETDIR.
        msilib.add_data(
            self.db,
            "Property",
            [("SecureCustomProperties", "TARGETDIR;REINSTALLMODE"), ("LAUNCHAPP", 1)],
        )
        msilib.add_data(
            self.db,
            "CustomAction",
            [
                ("A_SET_TARGET_DIR", 256 + 51, "TARGETDIR", self.initial_target_dir),
                ("A_SET_REINSTALL_MODE", 256 + 51, "REINSTALLMODE", "amus"),
                ("VSDCA_Launch", 210, "Subsearch.exe", ""),
            ],
        )
        msilib.add_data(
            self.db,
            "InstallExecuteSequence",
            [("A_SET_TARGET_DIR", 'TARGETDIR=""', 401), ("A_SET_REINSTALL_MODE", 'REINSTALLMODE=""', 402)],
        )
        msilib.add_data(
            self.db,
            "InstallUISequence",
            [
                ("PrepareDlg", None, 140),
                ("A_SET_TARGET_DIR", 'TARGETDIR=""', 401),
                ("A_SET_REINSTALL_MODE", 'REINSTALLMODE=""', 402),
                ("SelectDirectoryDlg", "not Installed", 1230),
                ("MaintenanceTypeDlg", "Installed and not Resume and not Preselected", 1250),
                ("ProgressDlg", None, 1280),
            ],
        )

    def add_exit_dialog(self):
        dialog = PyDialog(
            self.db,
            "ExitDialog",
            self.x,
            self.y,
            self.width,
            self.height,
            self.modal,
            self.title,
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
            "Launch App", 25, 130, 320, 30, 3, "Launch [ProductName] and Exit installer", None
        )
        launch_app.event("DoAction", "VSDCA_Launch", 'LAUNCHAPP="1"', "0")
        launch_app.event("EndDialog", "Return")
        dialog.backbutton("< Back", "Finish", active=False)
        dialog.cancelbutton("Cancel", "Back", active=False)
        dialog.text(
            "Description",
            15,
            235,
            320,
            20,
            0x30003,
            "Or click the Finish button exit the installer.",
        )
        button = dialog.nextbutton("Finish", "Cancel", name="Finish")
        # button.event("SetProperty", "VSDCA_Launch", "LAUNCHAPP", "1")
        # button.event("DoAction", "VSDCA_Launch", 'LAUNCHAPP="1"', '0')
        button.event("EndDialog", "Return")
