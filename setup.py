import sys

from cx_Freeze import Executable, setup

base = "Win32GUI" if sys.platform == "win32" else None

setup(
    options={
        "bdist_msi": {
            "upgrade_code": "{F12EBFBB-927E-4D29-818F-F26DB025D16C}",
            "install_icon": "src/subsearch/gui/assets/icon/subsearch.ico",
        },
    },
    executables=[
        Executable(
            "src/subsearch/__main__.py",
            base=base,
            target_name=f"Subsearch",
            icon="src/subsearch/gui/assets/icon/subsearch.ico",
            shortcut_name="Subsearch",
            shortcut_dir="ProgramMenuFolder",
        )
    ],
)
