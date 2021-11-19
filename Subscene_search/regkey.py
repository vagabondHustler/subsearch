from os import getcwd


def write_key():
    regkey_file = open('regkey.reg', 'w')
    regkey = r'''Windows Registry Editor Version 5.00

[HKEY_CLASSES_ROOT\Directory\Background\shell\Search subscene]
@=""
"Icon"="'''+str(getcwd()).replace('\\', '\\\\')+r'''\\resources\\icon.ico, 0"

[HKEY_CLASSES_ROOT\Directory\Background\shell\Search subscene\command]
@="cmd.exe \"%V\" /c  python '''+str(getcwd()).replace('\\', '\\\\')+r'\\main.pyw"'

    regkey_file.write(str(regkey))
    regkey_file.close()
