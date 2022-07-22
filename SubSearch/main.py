import sys

from src.utilities.local_paths import cwd, root_directory


def main() -> None:
    try:
        release_type = "major", "minor", "patch"
        if sys.argv[1] in release_type:
            from src.utilities.version import add_patch_minor_major

            add_patch_minor_major(sys.argv[1])
            return
    except IndexError:
        pass

    if cwd() == root_directory():
        import src.gui.settings_menu

        sys.exit()
    elif cwd() != root_directory():
        import src.subsearch

        src.subsearch.main()


if __name__ == "__main__":
    main()
