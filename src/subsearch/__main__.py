import sys

from gui import widget_settings
from utils import raw_registry, search


def main() -> None:
    r"""
    Usages: subsearch [OPTIONS]

    Options:
        --settings                                  Open the GUI settings menu

        --registry-key [add, del]                   Edit the registry
                                                    add: adds the context menu  / replaces the context menu with default values
                                                    del: deletes the context menu
                                                    e.g: subsearch --registry-key add

        --help                                      Prints usage information

        --search [release]                          Search for subtitles and download to current working directory
                                                    release: release.ext
                                                    e.g subsearch --search foo.bar.the.movie.2021.1080p.web-foobar.mkv
    """
    if sys.argv[-1].endswith("subsearch"):
        print(main.__doc__)
        return
    else:
        for num, arg in enumerate(sys.argv[1:], 1):
            if arg.startswith("--settings"):
                widget_settings.show_widget()
                break
            elif arg.startswith("--registry-key") or arg.startswith("--add-key"):
                if sys.argv[num + 1] == "add":
                    raw_registry.write_all_valuex()
                    break
                elif sys.argv[num + 1] == "del":
                    raw_registry.remove_context_menu()
                    break
            elif arg.startswith("--help"):
                print(main.__doc__)
                break
            elif arg.startswith("--search"):
                video_file = sys.argv[num + 1]
                search.run_search(video_file)
                break
            elif len(sys.argv[1:]) == num:
                print("Invalid argument")
                print(main.__doc__)


if __name__ == "__main__":
    main()
