import sys

from util import search, local_paths, current_user, raw_config, raw_registry
from gui import widget_settings


def main(input: str = None) -> None:
    """
    Args:
        input: --settings
    """
    if current_user.got_key() is False:
        raw_config.set_default_json()
        raw_registry.add_context_menu()

    if local_paths.get_path("cwd") == local_paths.get_path("root") or input == "--settings":
        widget_settings.show_widget()

    elif local_paths.get_path("cwd") != local_paths.get_path("root") and not sys.argv[-1].endswith(".py"):
        search.run_search(sys.argv[-1])


if __name__ == "__main__":
    main()
