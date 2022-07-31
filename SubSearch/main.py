import subprocess
import sys

from src.utilities import current_user, local_paths, read_config_json


def main():
    try:
        release_type = "major", "minor", "patch"
        if sys.argv[1] in release_type:
            from src.utilities.version import add_patch_minor_major

            add_patch_minor_major(sys.argv[1])
            return
    except IndexError:
        pass
    
    if local_paths.cwd() == local_paths.root_directory():
        # hides terminal window
        tf = read_config_json.get("terminal_focus")
        if str(sys.executable).endswith("python.exe") and tf == "False":
            if current_user.is_exe() is False:
                return subprocess.Popen(["pythonw", "main.py"])
        else:
            from src.gui import widget_settings
            widget_settings.show_widget()

    elif local_paths.cwd() != local_paths.root_directory():
        import src.subsearch

        src.subsearch.main()


if __name__ == "__main__":
    main()
