from importlib import util

cx_freeze_installed = util.find_spec("cx_Freeze")

def _cx_freeze():
    from cx_Freeze import Executable, setup

    icon = "src/subsearch/gui/assets/icon/subsearch.ico"
    bdist_msi_options = {"upgrade_code": "{F12EBFBB-927E-4D29-818F-F26DB025D16C}", "install_icon": icon}
    executable = [
        Executable(
            "src/subsearch/__main__.py",
            base="Win32GUI",
            target_name="Subsearch",
            icon=icon,
            shortcut_name="Subsearch",
            shortcut_dir="ProgramMenuFolder",
        ),
    ]
    setup(options={"bdist_msi": bdist_msi_options}, executables=executable)


def _setup_tools():
    import setuptools

    setuptools.setup()



def setup():
    if cx_freeze_installed:
        return _cx_freeze()  
    return _setup_tools()


if __name__ == "__main__":
    setup()
