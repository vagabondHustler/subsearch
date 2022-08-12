import os
import sys

from utils import current_user, local_paths, raw_config, raw_registry, search


def main() -> None:
    """
    main function of subsearch
    """
    for ext in raw_config.get("file_ext"):
        if sys.argv[-1].endswith(ext):
            file_full_path = sys.argv[-1]
            index = file_full_path.rfind("\\")
            file_path = file_full_path[0:index]
            file_name_ext = file_full_path[index + 1 :]
            os.chdir(file_path)

    if current_user.got_key() is False:
        raw_config.set_default_json()
        raw_registry.add_context_menu()
    if local_paths.cwd() == local_paths.get_path("root") or sys.argv[-1].endswith("subsearch.py"):
        from gui import widget_settings

        widget_settings.show_widget()
    elif local_paths.cwd() != local_paths.get_path("root"):
        search.run_search(file_name_ext, file_path)

    show_terminal = raw_config.get("show_terminal")
    if show_terminal:
        input()


if __name__ == "__main__":
    main()
