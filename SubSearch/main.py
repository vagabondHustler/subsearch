import sys

from src.utilities.local_paths import cwd, root_directory

# main
def main() -> None:
    if cwd() == root_directory():
        import src.gui.settings_menu

        sys.exit()
    elif cwd() != root_directory():
        import src.subsearch

        src.subsearch.main()


if __name__ == "__main__":
    main()
