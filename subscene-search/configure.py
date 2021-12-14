from src.current_user import is_admin
from src.current_user import got_key
from src.current_user import run_as_admin
from src.edit_config import select_language
from src.edit_config import select_precentage_pass
from src.edit_config import select_terminal_focus
from src.edit_config import select_cm_icon
from src.config import get
from src import registry


def menu(menu_option: int) -> str:
    if menu_option == 1:
        select_language()
    elif menu_option == 2:
        select_precentage_pass()
    elif menu_option == 3:
        select_terminal_focus()
        registry.write_command_subkey()
    elif menu_option == 4:
        select_cm_icon()
        registry.context_menu_icon()
    elif menu_option == 0:
        return "Exit"
    elif menu_option is not range(0, 4):
        print("Not a valid choice!")


def main() -> None:
    language, lang_abbr = get("language")
    precentage = get("percentage")
    focus = get("terminal_focus")
    icon = get("cm_icon")

    a = f"                       --- MENU ---                              \n"
    b = f"1. Change language                current: {language}, {lang_abbr}"
    c = f"2. Set search strictness          current: {precentage} out of 100%"
    d = f"3. Show Terminal on search        current: {focus}"
    e = f"4. Show context menu              current: {icon}"
    z = f"\nCtrl+C to exit\n"
    menu_options = [a, b, c, d, e, z]

    for item in menu_options:
        print(item)
    print("\n")
    try:
        option = int(input("Go to menu option: "))
    except ValueError:
        print("Invalid option")
        main()

    menu(option)
    main()


if is_admin():
    main()
elif got_key:
    run_as_admin()
else:
    print("Please run main.py first")
