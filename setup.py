from importlib import util



def _cx_freeze():
    """
    Builds an executable and MSI installer using cx_Freeze.

    """
    import os
    import sys

    from cx_Freeze import Executable, setup

    from subsearch.data import __guid__

    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

    icon = "src/subsearch/gui/resources/assets/subsearch.ico"
    app_name = "Subsearch"
    registry_path = rf"Software\Classes\*\shell\Subsearch"
    script_component = "_cx_executable0__Executable_script_src_subsearch___main__.py_"
    subsearch_key = (f"{app_name}_key", -1, registry_path, None, None, script_component)
    subsearch_icon = (f"{app_name}_regz_icon", -1, registry_path, "Icon", None, script_component)
    subsearch_appliesto = (f"{app_name}_regz_appliesto", -1, registry_path, "AppliesTo", None, script_component)
    subsearch_command = (f"{app_name}_key_command", -1, rf"{registry_path}\command", None, "", script_component)
    msi_data = {"Registry": {subsearch_key, subsearch_icon, subsearch_appliesto, subsearch_command}}

    bdist_msi_options = {"upgrade_code": f"{__guid__}", "install_icon": icon, "data": msi_data}

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
    """
    Builds the package using setuptools.

    """
    import setuptools

    setuptools.setup()


def setup():
    """
    Determines whether cx_Freeze is installed and calls the appropriate build function.

    """
    cx_freeze_installed = util.find_spec("cx_Freeze")
    if cx_freeze_installed:
        return _cx_freeze()
    return _setup_tools()


if __name__ == "__main__":
    setup()
