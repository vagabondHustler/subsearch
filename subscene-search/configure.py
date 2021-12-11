from src.os import root_directory_file
from src.edit_config import select_language
from src.edit_config import select_precentage_pass
from src.edit_config import select_terminal_focus
from src.config import get


# TODO: implement menu_option 3, 4


def menu(menu_option: int) -> str:
    if menu_option == 1:
        select_language()
    elif menu_option == 2:
        select_precentage_pass()
    elif menu_option == 3:
        print("Not yet implemented")
        # select_terminal_focus()1
    elif menu_option == 4:
        print("Not yet implemented")
    elif menu_option == 0:
        return "Exit"
    elif menu_option is not range(0, 4):
        print("Not a valid choice!")


def main() -> None:
    language, lang_abbr = get("language")
    precentage = get("percentage")
    focus = get("terminal_focus")
    icon = get("cm_icon")

    a = f"1. Set language                        current is {language}, {lang_abbr}\n"
    b = f"2. Set search strictness               current is {precentage} out of 100%\n"
    c = f"3. Set Terminal focus on search        current is {focus}\n"
    d = f"4. Set context_menu icon on/off        current is {icon}\n"
    z = f"\nCtrl+C to exit\n"
    menu_options = [a, b, c, d, z]

    for item in menu_options:
        print(item)
    print("\n")
    option = int(input("Enter number: "))
    menu(option)


if __file__ == root_directory_file("configure.py"):
    while True:
        e = main()
        if e == "Exit":
            break
