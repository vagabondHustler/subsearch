from src.local_paths import cwd, root_directory


def main() -> None:
    if cwd() == root_directory():
        import src.gui.settings_menu

        exit()
    elif cwd() != root_directory():
        import src.subsearch

        src.subsearch.main()


if __name__ == "__main__":
    main()
