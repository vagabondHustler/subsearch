import os                       # get cwd, rename files, make directories
import shutil                   # move .srt-files around
import regkey                   # .py file to write regkey.reg, easier than doing through winreg
import ctypes                   # run as admin
import sys                      # execute main.py
import winreg as reg            # check if sub keys already exists
from bs4 import BeautifulSoup   # webscraping
import requests                 # requests to urls
import time                     # sleep between requests, otherwise subscene times you out
import zipfile                  # unzipping downloaded .zip files


'''
    The standard for naming a scene release is typically by Title.Year.Soruce.Codec-GroupName, e.g foo.2021.1080p.WEB.H264-bar
    This standard can be used as a search parameter, we only need to fetch the path and directory name, then remove everything but the Title
'''


class Registry:
    def is_key(self) -> bool:       # check if keys exsist
        sub_key = r'Directory\Background\shell\Search subscene'             # registry path
        try:
            with reg.ConnectRegistry(None, reg.HKEY_CLASSES_ROOT) as hkey:
                reg.OpenKey(hkey, sub_key)
        except Exception:                                                   # raised if no key found
            return False

    def is_admin(self) -> bool:
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()        # check if script ran as admin, otherwise import .reg is denied
        except PermissionError:                                 # raise if user did not run as admin
            return False


class Search:
    def parameters(self, dir_name=os.getcwd(), season=False) -> list:   # cwd, e.g: C:/Users/username/Downloads/foo.2021.1080p.WEB.H264-bar
        temp_lst = []
        dir_name_lst = dir_name.split('\\')                     # removes / form the path to the directry e.g: 'C:' 'Users' 'username' 'Downloads' 'foo.2021.1080p.WEB.H264-bar'
        release_dot_name = dir_name_lst[-1]                     # get last part of the path which is the release name with . as spaces e.g: foo.2021.1080p.WEB.H264-bar
        release_name_lst = release_dot_name.split('.')          # remove . from the release name e.g: 'foo' '2021' '1080p' 'WEB' 'H264-bar'

        for word in release_name_lst:                           # loop through lst
            try:                                                # if word is not a int ValueError is raised
                int(word)
                year = word
                break                                           # if word = in, break, e.g year or quality
            except ValueError:
                temp_lst.append(word)                           # appends the Title to lst from the release name
                if word.startswith('s') or word.startswith('S') and word != release_name_lst[0]:  # s/S for season e.g Foo.Bar.s01e01
                    for letter in word[1]:                      # if second letter is not int continue
                        try:                                    # if word is not a int ValueError is raised
                            int(letter)
                            season = True
                            break
                        except ValueError:
                            pass
                title = ' '.join(temp_lst)
                if season is True:
                    break

        release_lst = dir_name_lst[-1].split('-')
        release_name = release_lst[0]
        scene_group = release_lst[1]
        name_group = dir_name_lst[-1]
        url = f'https://subscene.com/subtitles/searchbytitle?query={title}'

        try:
            year
        except NameError:
            year = None

        temp_lst = [url, title, year, release_name, scene_group, name_group]
        return temp_lst


class Values:
    s = Search()

    def __init__(self, values_lst=s.parameters()):
        self.values_lst = values_lst

    def values(self, use=None) -> str:
        if use == 'url':                                    # returns initial search url
            return self.values_lst[0]
        if use == 'title':                                  # returns release title e.g foo
            return self.values_lst[1]
        if use == 'year':                                   # returns the year of the release
            return self.values_lst[2]
        if use == 'release_name':                           # returns release name e.g foo.2021.1080p.WEB.H264-bar
            return self.values_lst[3]
        if use == 'scene_group':                            # returns the scene group e.g bar
            return self.values_lst[4]
        if use == 'name_group':                             # returns release name + scene group
            return self.values_lst[5]


class IsaMatch:
    def check(self, searched: str, search_result: str) -> int:      # compares searched words with words in result, returns int out of 100%
        match = 0
        searched: list = self.mk_lst(searched)
        search_result: list = self.mk_lst(search_result)
        greater_answer = self.is_bigger(searched, search_result)

        if len(searched) < len(search_result):                      # if one list is longer than the other _NONE gets added
            for ga in range(greater_answer):
                searched.append('_None')
        elif len(searched) > len(search_result):
            for ga in range(greater_answer):
                search_result.append('_None')
        else:
            pass

        for x, y in zip(searched, search_result):
            if self.compare(x, y) is True:
                match += 1
            else:
                pass

        tot = len(searched)
        percent_is = (round((match/tot)*100))

        return percent_is

    def find_res(self, word_lst) -> list:
        res_lst = ['4K', '2K', '4320p', '2160p', '1080p', '720p']
        count = 0

        for x in word_lst:
            if x in res_lst:
                count += 1
                res_lst.remove(x)
                release_res = x
                print(release_res)
        if count > 0:
            pass

    def mk_lst(self, x: str) -> list:
        x: list = x.split('.')
        x1 = x[-1].split('-')

        for item in x1:
            x.append(item)
        return x

    def is_bigger(self, searched, search_result) -> int:  # answer will not come back negative
        if len(searched) > len(search_result):
            answer = len(searched) - len(search_result)
            return answer
        elif len(searched) < len(search_result):
            answer = len(search_result) - len(searched)
            return answer

    def compare(self, x, y) -> bool:
        if x == y:
            return True
        else:
            return False


class Webscraping:
    v = Values()
    sm = IsaMatch()

    def __init__(self, title=v.values(use='title'),              # returns release title e.g foo
                 release_name=v.values(use='release_name'),      # for returning release_name e.g foo.2021.1080p.WEB.H264-bar
                 url=v.values(use='url'),                        # returns initial search url
                 scene_group=v.values(use='scene_group'),        # returns the scene group e.g bar
                 year=v.values(use='year'),                      # returns year of the release
                 name_group=v.values(use='name_group'),
                 sm=sm,
                 language='English',                             # language of the subtitles
                 search_title_lst=[], links_to_dl=[]):           # lsts

        self.title = title
        self.release_name = release_name
        self.url = url
        self.year = year
        self.scene_group = scene_group
        self.name_group = name_group
        self.language = language
        self.sm = sm
        self.search_title_lst = search_title_lst
        self.links_to_dl = links_to_dl

    def search_title(self) -> list:                                     # search with Search.parameter e.g directry name
        source = requests.get(self.url).text                            # inittial url request
        doc = BeautifulSoup(source, 'html.parser')                      # computing html
        search_result = doc.find('div', class_='search-result')         # section with search result from initial search
        sr_lis = [a for a in search_result.find_all('li') if a.text]    # url of subtitle matching title name
        for li in sr_lis:
            sr_href = li.find('a', href=True)
            print(self.year)
            if self.title in sr_href.text and self.year in sr_href.text:
                link = sr_href['href']
                self.search_title_lst.append(f'https://subscene.com/{link}')        # add missing address to url
            if len(self.search_title_lst) > 0:
                return self.search_title_lst
            else:
                pass

        links = [a['href'] for a in search_result.find_all('a', href=True) if a.text]   # url of subtitle matching title name

        for link in links:                                                              # place urls in said lst
            self.search_title_lst.append(f'https://subscene.com/{link}')                # add missing address to url

        number = len(self.search_title_lst)
        print(f"{number} titles matched '{self.title}'")
        print('------------------------------------------')

        if number == 0:
            exit('No matches')

        return self.search_title_lst

    def search_for_subtitles(self, number: int) -> list:              # check title and release name with subs list of avilable subtitles to download
        searching = True

        while searching is True:
            source = requests.get(self.search_title_lst[number]).text       # determin which url to request to from lst
            doc = BeautifulSoup(source, 'html.parser')
            tbody = doc.tbody                                               # tbody of html
            if tbody is not None:                                           # if subsceen returns 'to many requests' and timedout the connection, script does not crash
                tbc = tbody.contents                                        # contents of tbody
                searching = False
            else:
                time.sleep(2)                                               # takes around 2 seconds before a new request is allowd after 'to many requests'

        for content in tbc:
            if self.language in content.text:        # languish filter
                # remove spaces, tabs new-lines etc
                release_name = [
                    (x.text.replace('\r\n\t\t\t\t\t\t', '').replace(' \r\n\t\t\t\t\t', ''))
                    for x in content.find_all('span')
                ]
                link = [y['href'] for y in content.find_all('a', href=True) if y.text]        # url of downloadlink to subtitle matching release name)
                if self.sm.check(self.name_group, release_name[1]) >= 90:                     # checks if 90% of the words in searched and result are a match
                    if f'https://subscene.com/{link[0]}' not in self.links_to_dl:             # ignores already added subtitles in lst
                        self.links_to_dl.append(f'https://subscene.com/{link[0]}')
                else:
                    pass

        return self.links_to_dl

    def download_zip(self):     # download .zip files containing the subtitles
        number = 0
        subtitles_number = len(self.links_to_dl)
        print('\n')
        print(f'Downloading {subtitles_number} .zip files')
        print('------------------------------------------')

        for url in self.links_to_dl:                # lst containing urls with subtitles to download
            number += 1
            print(f'{number}/{subtitles_number}')
            save_path = os.getcwd()
            name = self.title.replace(' ', '_')     # name of the .zip file
            source = requests.get(url).text
            doc = BeautifulSoup(source, 'html.parser')
            link = [dl['href'] for dl in doc.find_all('a', href=True, id='downloadButton')]     # the download link of the .zip-file
            # remove spaces, tabs new-lines etc
            author = [
                (a.text.replace('A commentary by', '').replace('\n', '').replace('\r', '').replace('\t', '').replace(' ', ''))
                for a in doc.find_all('li', class_='author') if a.text
            ]
            zip_file = f'{save_path}\\{name}_by_{author[0]}_{number}.zip'       # name and path of .zip
            zip_file_url = f'https://subscene.com/{link[0]}'                    # add missing address to url
            r = requests.get(zip_file_url, stream=True)

            with open(zip_file, 'wb') as fd:                                    # save .zip with for loop
                for chunk in r.iter_content(chunk_size=128):
                    fd.write(chunk)

    def extract_zip(self):
        dir_name = os.getcwd()
        ext = ".zip"

        for item in os.listdir(dir_name):               # loop through items in dir
            if item.endswith(ext):                      # check for ".zip" extension
                file_name = os.path.abspath(item)       # get full path of files
                zip_ref = zipfile.ZipFile(file_name)    # create zipfile object
                zip_ref.extractall(f'{dir_name}')       # extract file to dir
                zip_ref.close()                         # close file
                os.remove(file_name)                    # delete zipped file

    def rename_srt(self):       # rename best matching .srt file so MPC auto-loads it, places rest of the .srt-files in /subs directory
        print('\n')
        subs = 'subs/'

        try:
            os.mkdir(subs)
        except FileExistsError:
            pass
        dir_name = os.getcwd()
        scene_group = self.scene_group
        preferred_ext = f'{scene_group}.srt'
        new_name = f'{self.name_group}.srt'
        ext = '.srt'

        for item in os.listdir(dir_name):
            if item.endswith(preferred_ext):
                try:
                    os.rename(item, new_name)
                except FileExistsError:
                    pass
                finally:
                    print(f'Added ~/{self.name_group}/{new_name}\nRemaining .srt moved to ~/{self.name_group}/subs\n')
                    break
            elif item.endswith(ext) and 'HI' not in item:
                try:
                    os.rename(item, new_name)
                except FileExistsError:
                    pass
                finally:
                    print(f'Added ~/{self.name_group}/{new_name}\nRemaining .srt moved to ~/{self.name_group}/subs\n')
                    break
            else:
                print(f'.srt moved to ~/{self.name_group}/subs\n')

        for item in os.listdir(dir_name):
            if item.endswith(ext) and not item.startswith(new_name):
                shutil.move(item, f'subs/{item}')


def main():     # main, checks if user is admin, if registry for contextmenu exists, runs webscraping etc...
    r = Registry()

    if r.is_admin():
        regkey.write_key()                              # regkey.reg gets written, adds a context menu option to start main.py when right clicking inside folder
        os.system('cmd /c "reg import regkey.reg"')     # imports regkey.reg to the registry
        exit(0)

    if r.is_key() is False:                             # check if key exists
        # Re-run the program with admin rights
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)  # runs script as admin if not admin

    else:
        w = Webscraping()
        w.search_title()
        urls_number = len(w.search_title_lst)
        if urls_number == 0:
            return exit('No subtitles found')

        for x in range(urls_number):
            print(f"Searching match: {x+1}/{urls_number}")
            w.search_for_subtitles(x)
            if len(w.links_to_dl) > 1:
                print(f"Subtitles found for '{w.name_group}'")
                break

            if x > urls_number:
                exit('No subtitles found')

        if len(w.links_to_dl) == 0:
            return exit(f'Nothing found for {w.release_name} by {w.scene_group}')

        w.download_zip()
        w.extract_zip()
        w.rename_srt()

        exit('--- All done ---')


main()
