import ctypes
import os
import webbrowser

from src.utilities import edit_registry
from src.utilities.current_user import got_key, is_admin, run_as_admin
from src.utilities.edit_config import select_cm_icon, select_hearing_impaired, select_language, select_precentage_pass, select_terminal_focus, set_default_values
from src.utilities.fetch_config import get
from src.utilities.updates import check_for_updates


def menu_options(menu_option: int) -> str:
    if menu_option == 1:
        select_language()
    elif menu_option == 2:
        select_precentage_pass()
    elif menu_option == 3:
        select_terminal_focus()
        edit_registry.write_command_subkey()
    elif menu_option == 4:
        select_cm_icon()
        edit_registry.context_menu_icon()
    elif menu_option == 5:
        select_hearing_impaired()
    elif menu_option == 6:
        os.system("cls||clear")
        check_for_updates()
        draw_menu()
    elif menu_option == 7:
        webbrowser.open("https://github.com/vagabondHustler/SubSearch/blob/main/README.md")
    elif menu_option == 0:
        return "Exit"
    elif menu_option is not range(0, 4):
        print("Not a valid choice!")


def draw_menu() -> None:
    if got_key() is False:
        set_default_values()
        edit_registry.add_context_menu()
    ctypes.windll.kernel32.SetConsoleTitleW("SubSearch - Menu")
    os.system("cls||clear")
    language, lang_abbr = get("language")
    precentage = get("percentage")
    focus = get("terminal_focus")
    hi = get("hearing_impaired")
    icon = get("cm_icon")

    a = f"                       --- MENU ---                              \n"
    b = f"1. Change language                            current: {language}, {lang_abbr}"
    c = f"2. Set precentage threshold                   current: {precentage}% out of 100%"
    d = f"3. Show Terminal on search                    current: {focus}"
    e = f"4. Show context menu icon                     current: {icon}"
    f = f"5. Use hearing impaired subtitles             current: {hi}"
    g = f"6. Check for updates"
    h = f"7. Help - Opens README.md in webbrowser"
    z = f"\nCtrl+C to exit\n"
    menu_options = [a, b, c, d, e, f, g, h, z]

    for item in menu_options:
        print(item)
    print("\n")
    try:
        option = int(input("Go to menu option: "))
    except ValueError:
        print("Invalid option")
        draw_menu()

    menu_options(option)
    draw_menu()


def main():
    if is_admin():
        draw_menu()
    elif got_key:
        run_as_admin()
    else:
        print("Please run main.py first")
