import sys

from src.utilities import local_paths


def main():
    if local_paths.get_path("cwd") == local_paths.get_path("root"):
        from src.gui import widget_settings

        widget_settings.show_widget()

    elif local_paths.get_path("cwd") != local_paths.get_path("root"):
        import src.subsearch

        src.subsearch.main(sys.argv[-1])


if __name__ == "__main__":
    main()

