from importlib import util

# TODO: Modify the MSI installer to add the correct registry key values without relying on the application to run once to generate them.
# Currently, the installer only adds registry key placeholders, which are updated only after the app runs and generates the correct values
# . 

def _cx_freeze():
    """
    Builds an executable and MSI installer using cx_Freeze.

    """
    from cx_Freeze import Executable, setup
    icon = "src/subsearch/gui/assets/icon/subsearch.ico"
    # Define registry keys and entries for context menu integration in Windows Explorer
    #
    # The context menu will be added to all file types. This can be later customized
    # inside the application itself, as the applicability of the context menu is associated
    # with file extensions and controlled by the `appliesto` entry in the registry.
    #
    # For more information on the MSI registry table, see:
    # https://learn.microsoft.com/en-us/windows/win32/msi/registry-table
    app_name = "Subsearch"
    registry_path = rf"Software\Classes\*\shell\Subsearch"
    script_component = "_cx_executable0__Executable_script_src_subsearch___main__.py_"
    subsearch_key = (f"{app_name}_key", -1, registry_path, None, None, script_component)
    subsearch_icon = (f"{app_name}_regz_icon", -1, registry_path, "Icon", None, script_component)
    subsearch_appliesto = (f"{app_name}_regz_appliesto", -1, registry_path, "AppliesTo", None, script_component)
    subsearch_command = (f"{app_name}_key_command", -1, rf"{registry_path}\command", None, "", script_component)

    msi_upgrade_code = "{F12EBFBB-927E-4D29-818F-F26DB025D16C}"
    msi_data = {"Registry": {subsearch_key, subsearch_icon, subsearch_appliesto, subsearch_command}}

    bdist_msi_options = {"upgrade_code": f"{msi_upgrade_code}", "install_icon": icon, "data": msi_data}

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
