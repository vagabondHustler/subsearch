from src.os import root_directory


regkey_deafult = (
    r"Windows Registry Editor Version 5.00" + "\n"
    r"" + "\n"
    r"[HKEY_CLASSES_ROOT\Directory\Background\shell\Search subscene]" + "\n"
    r'@=""' + "\n"
    r'"Icon"="' + str(root_directory()).replace("\\", "\\\\") + r'\\icon.ico, 0"' + "\n"
    r"" + "\n"
    r"[HKEY_CLASSES_ROOT\Directory\Background\shell\Search subscene\command]" + "\n"
    r'@="pwsh.exe -noexit -command \"& {$host.ui.RawUI.WindowTitle = ' + r"'Subscene search'" + r"}\" Set-Location -literalPath" + r" '%V'" + r"; python " + str(root_directory()).replace("\\", "\\\\") + r'\\main.py -NoNewWindow"' + "\n"
)


def write_key(focus="True", icon="True") -> None:

    with open("regkey.reg", "w") as f:
        line = r'"Icon"="' + str(root_directory()).replace("\\", "\\\\") + r'\\icon.ico, 0"' + "\n"
        reg_false_true = regkey_deafult
        _reg_true_true = regkey_deafult.replace("python", "pythonw")
        reg_true_true = _reg_true_true.replace("-noexit ", "")
        reg_false_false = reg_false_true.replace(line, "")
        reg_ture_false = regkey_deafult.replace(line, "")
        if focus == "True" and icon == "True":
            f.write(str(reg_true_true))

        if focus == "False" and icon == "False":
            f.write(str(reg_false_false))

        if focus == "True" and icon == "False":
            f.write(str(reg_ture_false))

        if focus == "False" and icon == "True":
            f.write(str(reg_false_true))
