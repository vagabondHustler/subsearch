import sys

from gui import widget_settings
from utils import current_user, local_paths, raw_config, raw_registry, search


def main(enter: str = None) -> None:
    """
    main function for subsearch

    Parameters
    ----------
    input : str, optional
        --settings, by default None
        if sys.argv[1] == "subsearch.py", enter = "--settings":

    """
    if current_user.got_key() is False:
        raw_config.set_default_json()
        raw_registry.add_context_menu()
    if sys.argv[-1].endswith("subsearch.py"):
        enter = "--settings"
    if local_paths.get_path("cwd") == local_paths.get_path("root") or enter == "--settings":
        widget_settings.show_widget()

    elif local_paths.get_path("cwd") != local_paths.get_path("root"):
        search.run_search(sys.argv[-1])


if __name__ == "__main__":
    main()
