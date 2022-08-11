import os
import sys

from gui import widget_settings
from utils import current_user, local_paths, raw_config, raw_registry, search


def main() -> None:
    """
    main function for subsearch

    Parameters
    ----------
    input : str, optional
        --settings, by default None
        if sys.argv[1] == "subsearch.py", enter = "--settings":

    """

    for ext in raw_config.get("file_ext"):
        if sys.argv[-1].endswith(ext):
            file_path = sys.argv[-1]
            index = file_path.rfind("\\")
            dir_path = file_path[0:index]
            os.chdir(dir_path)

    if current_user.got_key() is False:
        raw_config.set_default_json()
        raw_registry.add_context_menu()
    if local_paths.get_path("cwd") == local_paths.get_path("root") or sys.argv[-1].endswith("subsearch.py"):
        widget_settings.show_widget()
    elif local_paths.get_path("cwd") != local_paths.get_path("root"):
        search.run_search(sys.argv[-1])


if __name__ == "__main__":
    main()
