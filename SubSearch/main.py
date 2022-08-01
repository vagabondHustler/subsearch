import subprocess
import sys

from src.utilities import current_user, local_paths, read_config


def main():
    if current_user.is_exe() is False:
        show_terminal = read_config.get("show_terminal")
        if str(sys.executable).endswith("python.exe") and show_terminal == "False":
            return subprocess.Popen(["pythonw", "main.py"])
    if local_paths.cwd() == local_paths.root_directory():
        from src.gui import widget_settings

        widget_settings.show_widget()

    elif local_paths.cwd() != local_paths.root_directory():
        import src.subsearch

        src.subsearch.main(sys.argv[-1])


if __name__ == "__main__":
    main()
