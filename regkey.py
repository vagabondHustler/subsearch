from os import getcwd

cwd = getcwd()


def write():
    regkey_file = open('regkey.reg', 'w')
    regkey = r'''Windows Registry Editor Version 5.00

[HKEY_CLASSES_ROOT\Directory\Background\shell\Search subscene]
@=""
"Icon"="'''+str(cwd()).replace('\\', '\\\\')+r'''\\resources\\icon.ico, 0"

[HKEY_CLASSES_ROOT\Directory\Background\shell\Search subscene\command]
@="cmd.exe \"%V\" /c  python '''+str(cwd()).replace('\\', '\\\\')+r'\\main.py"'

    regkey_file.write(str(regkey))
    regkey_file.close()
