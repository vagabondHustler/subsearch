from src.os import root_directory


regkey = (
    r"Windows Registry Editor Version 5.00" + "\n"
    r"" + "\n"
    r"[HKEY_CLASSES_ROOT\Directory\Background\shell\Search subscene]" + "\n"
    r'@=""' + "\n"
    r'"Icon"="' + str(root_directory()).replace("\\", "\\\\") + r'\\icon.ico, 0"' + "\n"
    r"" + "\n"
    r"[HKEY_CLASSES_ROOT\Directory\Background\shell\Search subscene\command]" + "\n"
    r'@="cmd.exe \"%V\" /c start /min python ' + str(root_directory()).replace("\\", "\\\\") + r'\\main.py"' + "\n"
)


def write_key() -> None:
    with open("regkey.reg", "w") as f:
        f.write(str(regkey))
