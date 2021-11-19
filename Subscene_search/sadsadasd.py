import os                       # get cwd
import regkey                   # .py file to write regkey.reg, easier than doing through winreg
import ctypes                   # run as admin
import sys                      # execute main.py
import winreg as reg            # check if sub keys allready exists
from bs4 import BeautifulSoup
import requests


'''
    The standard for naming a scene release is typically by Title.Year.Soruce.Codec-GroupName, e.g foo.2021.1080p.WEB.H264-bar
    This standard can be used as a search parameter, we only need to fetch the path and directory name, then remove everything but the Title
'''


def cwd():
    dir_name = os.getcwd()
    return dir_name     # return path, used in Search.parameter


class Search:
    def parameter(self, dir_name=cwd(), release_title_lst=[], full=False):       # cwd, e.g: C:/Users/username/Downloads/foo.2021.1080p.WEB.H264-bar
        dir_name_lst = dir_name.split('\\')                                     # removes / form the path to the directry e.g: 'C:' 'Users' 'username' 'Downloads' 'foo.2021.1080p.WEB.H264-bar'
        release_dot_name = dir_name_lst[-1]                                     # get last part of the path which is the release name with . as spaces e.g: foo.2021.1080p.WEB.H264-bar
        release_name_lst = release_dot_name.split('.')                          # remove . from the release name e.g: 'foo' '2021' '1080p' 'WEB' 'H264-bar'
        if full is True:
            print('test')
            return dir_name_lst[-1]
        for word in release_name_lst:                                           # loop through lst
            try:                                                                # if word is not a int ValueError is raised
                int(word)
                break                                                           # if word is a in break
            except ValueError:
                release_title_lst.append(word)                                  # appends the Title to lst from the release name
                if len(release_title_lst) <= 1:
                    name = word
                else:
                    name = ' '.join(release_title_lst)

        print(f'in parameters {name}')
        return name

    def subscene(self, name_of_release: str):
        url = f'https://subscene.com/subtitles/searchbytitle?query={name_of_release}'
        print(f'subscene {url}')
        return url                                                  # returns name of release with year eg 'foo'


class Webscraping:
    def search_results(self, url=None, title=None, link_lst=[]):
        print(f'printing url:{url}')
        source = requests.get(url).text
        doc = BeautifulSoup(source, 'html.parser')
        search_result = doc.find('div', class_='search-result')
        results = [r.text for r in search_result.find_all('a')]
        links = [a['href'] for a in search_result.find_all('a', href=True) if a.text]
        for result, link in zip(results, links):
            link_lst.append(f'https://subscene.com/{link}')
        number = len(link_lst)
        print(f'Found {number} titles that match')
        print('\n')
        return link_lst

    def find_subtitle(self, link_lst=None, name=None, links_to_dl=[]):
        number = 0
        for url in link_lst:
            number += 1
            print(f'Checking title {number} for subtitles')
            try:
                source = requests.get(url).text
                doc = BeautifulSoup(source, 'html.parser')
                tbody = doc.tbody
                trs = tbody.contents
                for tr in trs:
                    if 'English' in tr.text:
                        release_name = [(x.text.replace('\r\n\t\t\t\t\t\t', '').replace(' \r\n\t\t\t\t\t', '')) for x in tr.find_all('span')]
                        link = [y['href'] for y in tr.find_all('a', href=True) if y.text]
                        if name in release_name[1]:
                            # print(f'{release_name[1]}\nhttps://subscene.com/{link[0]}\n\n')
                            links_to_dl.append(f'https://subscene.com/{link[0]}')
            except AttributeError:
                pass
        print('\n')
        return links_to_dl

    def download_sub(self, name=None, lst=None):
        print('Gathering download links\n\n')
        number = 0
        for url in lst:
            number += 1
            save_path = cwd()
            name = name.replace(' ', '_')
            zip_file = f'{save_path}\\{name}_{number}.zip'
            try:
                source = requests.get(url).text
                doc = BeautifulSoup(source, 'html.parser')
                link = [dl['href'] for dl in doc.find_all('a', href=True, id='downloadButton')]
                print(f'Downloading subtitles for {name} as {name}_{number}.zip')
                zip_file_url = f'https://subscene.com/{link[0]}'
                r = requests.get(zip_file_url, stream=True)
                with open(zip_file, 'wb') as fd:
                    for chunk in r.iter_content(chunk_size=128):
                        fd.write(chunk)
                # dl_link = [dl['href'] for dl in doc.find_all('a', href=True) if dl.text]
                # print(dl_link)

            except AttributeError:
                pass


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


r = Registry()
s = Search()
w = Webscraping()


if r.is_admin():
    regkey.write_key()                              # regkey.reg gets written, adds a context menu option to start main.py when right clicking inside folder
    os.system('cmd /c "reg import regkey.reg"')     # imports regkey.reg to the registry
if r.is_key() is False:                             # check if key exists
    # Re-run the program with admin rights
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)  # runs script as admin if not admin
else:
    w.download_sub(name=s.parameter(full=False),
                   lst=w.find_subtitle(link_lst=w.search_results(url=s.subscene(s.parameter()), title=s.subscene(s.parameter())), name=s.parameter(full=True)
                                       )
                   )

    pass
input('')

# try:
#     for link in links:
#         print(link)
# except TypeError:
#     pass

# for link in links:
#     print(link)
#     w.find_subtitle(link)
# w.find_subtitle('https://subscene.com/subtitles/stillwater-2021')


# class Search:
#     def parameter(self, name=None, dir_name=cwd(), send=None, release_title_lst=[]):       # cwd, e.g: C:/Users/username/Downloads/foo.2021.1080p.WEB.H264-bar
#         dir_name_lst = dir_name.split('\\')                                     # removes / form the path to the directry e.g: 'C:' 'Users' 'username' 'Downloads' 'foo.2021.1080p.WEB.H264-bar'
#         release_dot_name = dir_name_lst[-1]                                     # get last part of the path which is the release name with . as spaces e.g: foo.2021.1080p.WEB.H264-bar
#         release_name_lst = release_dot_name.split('.')                          # remove . from the release name e.g: 'foo' '2021' '1080p' 'WEB' 'H264-bar'
#         for word in release_name_lst:                                           # loop through lst
#             try:                                                                # if word is not a int ValueError is raised
#                 int(word)
#                 break                                                           # if word is a in break
#             except ValueError:
#                 print(word)
#                 release_title_lst.append(word)                                  # appends the Title to lst from the release name
#                 if len(release_title_lst) >= 1:
#                     name = word
#                 else:
#                     name = ' '.join(release_title_lst)
#
#         if send == 'scene_name':
#             release_name = dir_name_lst[-1]
#             print(f'Returning Release name: {release_name}')
#             return release_name
#         if send == 'name':
#             print(f'Returning name: {name}')
#             return name
#         if send == 'url':
#             url = f'https://subscene.com/subtitles/searchbytitle?query={name}'
#             print(f'Returning url: {url}')
#             return url
