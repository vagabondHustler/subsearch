import sys

from gui import widget_settings
from utils import raw_registry


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
    """
    if sys.argv[-1].endswith("subsearch"):
        print(main.__doc__)
        return
    else:
        for num, arg in enumerate(sys.argv[1:], 1):
            if arg.startswith("--settings"):
                sys.argv.pop(num)
                widget_settings.show_widget()
                break
            elif arg.startswith("--registry-key") or arg.startswith("--add-key"):
                if sys.argv[num + 1] == "add":
                    sys.argv.pop(num)  # remove registry argument
                    sys.argv.pop(num)  # remove add argument
                    raw_registry.add_context_menu()
                    break
                elif sys.argv[num + 1] == "del":
                    sys.argv.pop(num)  # remove registry argument
                    sys.argv.pop(num)  # remove del argument
                    raw_registry.remove_context_menu()
                    break
            elif arg.startswith("--help"):
                sys.argv.pop(num)
                print(main.__doc__)
                break
            elif len(sys.argv[1:]) == num:
                print("Invalid argument")
                print(main.__doc__)
