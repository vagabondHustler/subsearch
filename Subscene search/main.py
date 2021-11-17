import webbrowser               # open website URL in deafult browser
import os                       # get cwd
import regkey                   # .py file to write regkey.reg, easier than doing through winreg
import ctypes                   # run as admin
import sys                      # execute main.py
import winreg as reg            # check if sub keys allready exists
from bs4 import BeautifulSoup
import requests

if __name__ == '__main__':
    regkey

'''
    The standard for naming a scene release is typically by Title.Year.Soruce.Codec-GroupName, e.g foo.2021.1080p.WEB.H264-bar
    This standard can be used as a search parameter, we only need to fetch the path and directory name, then remove everything but the Title
'''


def cwd():
    dir_name = os.getcwd()
    return dir_name     # return path, used in Search.parameter


class Search:
    def parameter(self, dir_name: str, release_title_lst=[]):       # cwd, e.g: C:/Users/username/Downloads/foo.2021.1080p.WEB.H264-bar
        dir_name_lst = dir_name.split('\\')                         # removes / form the path to the directry e.g: 'C:' 'Users' 'username' 'Downloads' 'foo.2021.1080p.WEB.H264-bar'
        release_dot_name = dir_name_lst[-1]                         # get last part of the path which is the release name with . as spaces e.g: foo.2021.1080p.WEB.H264-bar
        release_name_lst = release_dot_name.split('.')              # remove . from the release name e.g: 'foo' '2021' '1080p' 'WEB' 'H264-bar'
        for word in release_name_lst:                               # loop through lst
            try:                                                    # if word is not a int ValueError is raised
                int(word)
                break                                               # if word is a in break
            except ValueError:
                release_title_lst.append(word)                      # appends the Title to from the release name
        name_of_release = ' '.join(release_title_lst)               # join the lst into str with spaces between words
        return name_of_release

    def subscene(self, name_of_release: str):
        query = 'https://subscene.com/subtitles/searchbytitle?query='
        url = f'{query}{name_of_release}'
        return url                                                  # returns name of release with year eg 'foo'


class Registry:
    def is_key(self):   # check if keys exsist
        sub_key = r'Directory\Background\shell\Search subscene'             # registry path
        try:
            with reg.ConnectRegistry(None, reg.HKEY_CLASSES_ROOT) as hkey:
                reg.OpenKey(hkey, sub_key)
        except Exception:                                                   # raised if no key found
            return False

    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()        # check if script ran as admin, otherwise import .reg is denied
        except PermissionError:                                 # raiser if user did not run as admin
            return False


# r = Registry()
s = Search()
# if r.is_admin():
#     regkey.write_key()                              # regkey.reg gets written, adds a context menu option to start main.py when right clicking inside folder
#     os.system('cmd /c "reg import regkey.reg"')     # imports regkey.reg to the registry
# if r.is_key() is False:                             # check if key exists
#     # Re-run the program with admin rights
#     ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)  # runs script as admin if not admin
# else:
#     url = s.subscene(s.parameter(cwd()))
#     webbrowser.open(url)
#     exit(0)


class Webscraping:
    def request(self):
        url = s.subscene(s.parameter('The Dark Knight'))
        source = requests.get(url).text
        soup = BeautifulSoup(source, 'html.parser')
        best_result = soup.find('div', class_='byTitle')
        for result in best_result:
            href = result.find('a')['href']
            print(f'\n{href}\n')
        # best_h2 = best_result.h2.text
        # best_ul = best_result.ul.text
        # print(best_h2, best_ul)
        # for close_result in soup.find_all('div', class_='close'):
        #     close_h2 = close_result.h2.text
        #     close_ul = close_result.ul.text
        #     print(close_h2, close_ul)


w = Webscraping()
w.request()
