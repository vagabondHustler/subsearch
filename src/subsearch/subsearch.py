import os
import sys

from gui import widget_settings
from utils import current_user, raw_config, raw_registry, search


def main() -> None:
    """
    main function of subsearch
    """
    file_path = ""
    file_name_ext = ""
    file_exist = False
    if current_user.got_key() is False:
        raw_config.set_default_json()
        raw_registry.add_context_menu()
    if current_user.check_is_exe():
        raw_config.set_json("show_terminal", False)
    show_terminal = raw_config.get("show_terminal")
    for ext in raw_config.get("file_ext"):
        if sys.argv[-1].endswith(ext):
            file_exist = True
            file_full_path = sys.argv[-1]
            index = file_full_path.rfind("\\")
            file_path = file_full_path[0:index]
            file_name_ext = file_full_path[index + 1 :]
            os.chdir(file_path)
            break

    if file_exist is False:
        widget_settings.show_widget()

    if file_exist:
        search.run_search(file_name_ext, file_path)

    if show_terminal is True:
        input()


if __name__ == "__main__":
    main()
