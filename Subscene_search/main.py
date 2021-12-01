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
import tkinter as tk            # for Gui
from tkinter import Label, Button, Scrollbar, Listbox, END  # for Gui functionality
from ctypes import windll       # for removing title bar etc
import threading                # so script and Gui can run at the same time

'''
    The standard for naming a scene release is typically by Title.Year.Soruce.Codec-GroupName, e.g foo.2021.1080p.WEB.H264-bar
    This standard can be used as a search parameter, we only need to fetch the path and directory name, then remove everything but the Title
'''

cwd = os.getcwd()


def rwd():
    root_dir_path, _file_name = os.path.split(os.path.abspath(__file__))      # allows file being in read from orgin while in working folder
    language_file = f'{root_dir_path}\\language'
    return language_file


def listbox_select(x, select=END):
    x.select_clear(x.size() - 2)      # Clear the current selected item
    x.select_set(select)              # Select the new item
    x.yview(select)


class Gui():    # main gui
    def __init__(self, master,
                 mbc='#191919', bg='#121212', fg='#797979', bgc='#23252C', abg='#131313', hc='#24272E', sbgc='#240d14',  # colors for Gui
                 font8='Cascadia 8 bold', font10='Cascadia 10 bold'):   # fonts
        self.master = master
        self.mbc = mbc
        self.bg = bg
        self.fg = fg
        self.bgc = bgc
        self.abg = abg
        self.hc = hc
        self.sbgc = sbgc
        self.font8 = font8
        self.font10 = font10

        # main window settings
        master.geometry(self.tkpos(self.master))
        master.configure(borderwidth=0, relief='flat', highlightthickness=0, background=self.mbc)
        master.resizable(False, False)
        master.wm_title("Subscene_search")
        master.overrideredirect(True)
        master.after(10, self.set_appwindow, master)
        master.attributes('-topmost', 1)
        master.focus_force()

        # custom window label
        titlebar_canvas = tk.Canvas(master, height=24, width=1060)
        titlebar_canvas.configure(highlightthickness=0, bg=self.bg)
        titlebar_canvas.place(relx=0, rely=0, anchor='nw')
        titlebar_canvas.bind('<Button-1>', self.click)
        titlebar_canvas.bind('<B1-Motion>', self.drag)

        # draw app name, language menu and exit button in corner
        self.app_name(self.master)
        self.language_menu(self.master)
        self.button_exit(self.master)

        # starts main script and Gui terminal
        t1 = threading.Thread(target=script)
        t2 = threading.Thread(target=RedirectTerminal)
        t1.start()
        t2.start()
        t2.join()
        master.protocol("WM_DELETE_WINDOW", self.exit_terminal)   # when user presses corner x windows will close

    def exit_terminal(self):
        exit()

    def button_exit(self, master):                  # exit button
        def on_enter(self):                         # button light up when mouseover
            button_exit['background'] = '#252525'

        def on_leave(self):
            button_exit['background'] = '#121212'

        # exit button settings
        button_exit = Button(master, text='X', command=master.destroy, height=1, width=3, bd=0,
                             bg=self.bg, activebackground=self.abg, fg=self.fg,  font=self.font10)
        button_exit.place(relx=1, rely=0, anchor='ne')
        button_exit.bind("<Enter>", on_enter)
        button_exit.bind("<Leave>", on_leave)

    def app_name(self, master):         # title of window
        label = Label(master, text='Subscene search', height=1)
        label.configure(bg=self.bg, fg=self.fg, font=self.font8)
        label.place(relx=0, rely=0.0046, anchor='nw')

    def language_menu(self, master):            # language
        rt = RedirectTerminal()                     # custom print class

        def select(self):                   # allows selection of language from list
            selection = lb.curselection()
            value = lb.get(selection[0])
            with open(rwd(), 'w') as f:
                f.write(value)
            rt.output(f'You have selected {value} as your language')

        language = ['Arabic',
                    'Bengali',
                    'Brazillian/Portuguese',
                    'Danish',
                    'Dutch',
                    'English',
                    'Farsi/Persian',
                    'Finnish',
                    'French',
                    'German',
                    'Greek',
                    'Hebrew',
                    'Indonesian',
                    'Italian',
                    'Korean',
                    'Malay',
                    'Norwegian',
                    'Portuguese',
                    'Romanian',
                    'Spanish',
                    'Swedish',
                    'Thai',
                    'Turkish',
                    'Vietnamese']

        sb = Scrollbar(master, bg=self.bg)              # allows scrolling in language list
        sb.place(relx=2, rely=2, anchor='center')

        lb = Listbox(master, height=24, selectmode='single', yscrollcommand=sb.set, exportselection=False, activestyle='none')

        for lang in language:
            lb.insert(END, lang)

        lb.configure(bd=0, highlightthickness=0,
                     bg=self.bg, fg=self.fg, highlightcolor=self.hc, selectbackground=self.sbgc,  selectforeground=self.fg, font=self.font8)
        lb.grid(column=1, pady=30, row=1)

        # highlight current language
        if os.path.isfile(rwd()):
            with open(rwd(), 'r') as f:
                lines = f.readlines()
                lang = [line.rstrip() for line in lines]
                for n in enumerate(language):
                    if lang[0] == n[1]:
                        listbox_select(lb, select=n[0])
        lb.bind('<<ListboxSelect>>', select)

    def tkpos(self, master, w=858, h=396):              # centers the window in the middle of the screeen
        # get screen width and height
        ws = master.winfo_screenwidth()       # width of the screen
        hs = master.winfo_screenheight()      # height of the screen

        # calculate x and y coordinates for the Tk root window
        x = int((ws/2) - (w/2))
        y = int((hs/2) - (h/2))
        value = f'{w}x{h}+{x}+{y}'
        return value

    def set_appwindow(self, master):                        # for removing original window border and title bar
        GWL_EXSTYLE = -20
        WS_EX_APPWINDOW = 0x00040000
        WS_EX_TOOLWINDOW = 0x00000080
        hwnd = windll.user32.GetParent(master.winfo_id())
        style = windll.user32.GetWindowLongPtrW(hwnd, GWL_EXSTYLE)
        style = style & ~WS_EX_TOOLWINDOW
        style = style | WS_EX_APPWINDOW
        # res = windll.user32.SetWindowLongPtrW(hwnd, GWL_EXSTYLE, style)
        # re-assert the new window style
        master.withdraw()
        master.after(10, master.deiconify)

    def drag(self, event):                              # allows title bar to be clicked and dragged
        x = self.master.winfo_pointerx() - offsetx      # calculate mouse pos before and after click
        y = self.master.winfo_pointery() - offsety
        self.master.geometry('+{x}+{y}'.format(x=x, y=y))

    def click(self, event):
        global offsetx, offsety
        offsetx = event.x
        offsety = event.y

    offsetx = 0
    offsety = 0


class RedirectTerminal():             # class for printing to Gui terminal
    def lbc_listbox(self):
        global lbc
        lbc = Listbox(root, height=24, width=120, selectmode='single', exportselection=False, activestyle='none')
        lbc.configure(bd=0, highlightthickness=0,
                      bg='#121212', fg='#797979', highlightcolor='#121212', selectbackground='#240d14', selectforeground='#797979', font='Cascadia 8 bold')
        lbc.grid(column=0, padx=6, pady=30, row=1)

    def output(self, x, newline=True):
        if newline is False and x != '':
            lbc.delete(END)
        lbc.insert(END, f'  {x}')           # insert from _output_lst
        listbox_select(lbc)
        if '--- All done ---' == x:
            for number in range(10, -1, -1):
                if number == 0:
                    break
                lbc.insert(END, f'  Auto exit in {number} seconds')
                listbox_select(lbc)
                time.sleep(1)
                label_item = f'  Auto exit in {number} seconds'
                idx = lbc.get(0, END).index(label_item)
                lbc.delete(idx)
            root.quit()
            os._exit(1)


class CurrentUser:
    def got_key(self) -> bool:       # check if keys exsist
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

    def got_file(self) -> bool:
        if os.path.isfile(rwd()) and os.stat(rwd()).st_size != 0:
            return True
        else:
            return False


class FilterOut:
    def __init__(self, dir_name=cwd):
        self.dir_name = dir_name

    def dir_path(self, season=False) -> list:   # cwd, e.g: C:/Users/username/Downloads/foo.2021.1080p.WEB.H264-bar
        _lst = []
        dir_name_lst = self.dir_name.split('\\')                # removes / form the path to the directry e.g: 'C:' 'Users' 'username' 'Downloads' 'foo.2021.1080p.WEB.H264-bar'
        release_dot_name = dir_name_lst[-1]                     # get last part of the path which is the release name with . as spaces e.g: foo.2021.1080p.WEB.H264-bar
        release_name_lst = release_dot_name.split('.')          # remove . from the release name e.g: 'foo' '2021' '1080p' 'WEB' 'H264-bar'
        for word in release_name_lst:                           # loop through lst
            try:                                                # if word is not a int ValueError is raised
                int(word)
                year = word
                break                                           # if word = in, break, e.g year or quality
            except ValueError:
                _lst.append(word)                           # appends the Title to lst from the release name
                if word.startswith('s') or word.startswith('S') and word != release_name_lst[0]:  # s/S for season e.g Foo.Bar.s01e01
                    for letter in word[1]:                      # if second letter is not int continue
                        try:                                    # if word is not a int ValueError is raised
                            int(letter)
                            season = True
                            break
                        except ValueError:
                            season = False
                            pass
                title = ' '.join(_lst)
                if season is True:
                    break
        release_lst = dir_name_lst[-1].split('-')
        release_name = release_lst[0]
        scene_group = release_lst[-1]
        name_group = dir_name_lst[-1]
        url = f'https://subscene.com/subtitles/searchbytitle?query={title}'
        try:
            year
        except NameError:
            year = 'N/A'

        _lst = [url, title, year, release_name, scene_group, name_group, season]
        return _lst


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

    # def find_res(self, word_lst) -> list:
    #     res_lst = ['4K', '2K', '4320p', '2160p', '1080p', '720p']
    #     count = 0
    #
    #     for x in word_lst:
    #         if x in res_lst:
    #             count += 1
    #             res_lst.remove(x)
    #
    #     if count > 0:
    #         pass

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
        if x.lower() == y.lower():      # compare serched with results, lowercase
            return True
        else:
            return False


class ReturnValues:
    fo = FilterOut()
    rt = RedirectTerminal()

    def __init__(self, directory_path=fo.dir_path()):
        self.directory_path = directory_path

    def from_dir(self, use=None) -> str:
        if use == 'url':                                    # returns initial search url
            return self.directory_path[0]
        if use == 'title':                                  # returns release title e.g foo
            return self.directory_path[1]
        if use == 'year':                                   # returns the year of the release
            return self.directory_path[2]
        if use == 'release_name':                           # returns release name e.g foo.2021.1080p.WEB.H264-bar
            return self.directory_path[3]
        if use == 'scene_group':                            # returns the scene group e.g bar
            return self.directory_path[4]
        if use == 'name_group':                             # returns release name + scene group
            return self.directory_path[5]
        if use == 'season':
            return self.directory_path[6]


class WebScraping:
    rv = ReturnValues()
    sm = IsaMatch()
    rt = RedirectTerminal()

    def __init__(self, title=rv.from_dir(use='title'),           # returns release title e.g foo
                 release_name=rv.from_dir(use='release_name'),   # for returning release_name e.g foo.2021.1080p.WEB.H264-bar
                 url=rv.from_dir(use='url'),                     # returns initial search url
                 scene_group=rv.from_dir(use='scene_group'),     # returns the scene group e.g bar
                 name_group=rv.from_dir(use='name_group'),       # returns name with group
                 year=rv.from_dir(use='year'),                   # returns year of the release
                 season=rv.from_dir(use='season'),               # if dir is part of a show, value is True
                 accuracy=90,                                    # defines how many% of the words in the title, which need to match the search result
                 sm=sm,
                 rt=rt,
                 search_title_lst=[], links_to_dl=[]):           # lsts

        self.title = title
        self.release_name = release_name
        self.url = url
        self.year = year
        self.scene_group = scene_group
        self.name_group = name_group
        self.season = season
        self.accuracy = accuracy
        self.sm = sm
        self.rt = rt
        self.search_title_lst = search_title_lst
        self.links_to_dl = links_to_dl

    def search_title(self) -> list:                                     # search with Search.parameter e.g directry name
        source = requests.get(self.url).text                            # inittial url request
        doc = BeautifulSoup(source, 'html.parser')                      # computing html
        search_result = doc.find('div', class_='search-result')         # section with search result from initial search
        sr_lis = [a for a in search_result.find_all('li') if a.text]    # url of subtitle matching title name
        for li in sr_lis:
            sr_href = li.find('a', href=True)
            if self.season is False:
                if self.title.lower() in sr_href.text.lower() and self.year in sr_href.text:
                    link = sr_href['href']
                    self.search_title_lst.append(f'https://subscene.com/{link}')        # add missing address to url
            elif self.season is True:
                links = [a['href'] for a in search_result.find_all('a', href=True) if a.text]   # url of subtitle matching title name

                for link in links:                                                              # place urls in said lst
                    if link not in self.search_title_lst:
                        self.search_title_lst.append(f'https://subscene.com/{link}')            # add missing address to url

        number = len(self.search_title_lst)
        self.rt.output('')
        self.rt.output(f"{number} titles matched '{self.title}'")

        if number == 0:
            return None

        return self.search_title_lst

    def search_for_subtitles(self, number: int) -> list:              # check title and release name with subs list of avilable subtitles to download
        searching = True

        while searching is True:
            source = requests.get(self.search_title_lst[number]).text       # determin which url to request to from lst
            doc = BeautifulSoup(source, 'html.parser')
            tbody = doc.tbody                 # tbody of html
            if tbody is not None:             # if subsceen returns 'to many requests' and timedout the connection, script does not crash
                tbc = tbody.contents          # contents of tbody
                searching = False
            else:
                time.sleep(1)                 # takes around 2 seconds before a new request is allowd after 'to many requests'

        for content in tbc:
            with open(rwd(), 'r') as f:
                lines = f.readlines()
                lines = [line.rstrip() for line in lines]
            if lines[0] in content.text:        # languish filter
                # remove spaces, tabs new-lines etc
                release_name = [
                    (x.text.replace('\r\n\t\t\t\t\t\t', '').replace(' \r\n\t\t\t\t\t', ''))
                    for x in content.find_all('span')
                ]
                link = [y['href'] for y in content.find_all('a', href=True) if y.text]        # url of downloadlink to subtitle matching release name)
                if self.sm.check(self.name_group, release_name[1]) >= self.accuracy:          # checks if 90% of the words in searched and result are a match
                    if f'https://subscene.com/{link[0]}' not in self.links_to_dl:             # ignores already added subtitles in lst
                        self.links_to_dl.append(f'https://subscene.com/{link[0]}')
                else:
                    pass

        return self.links_to_dl

    def download_zip(self):     # download .zip files containing the subtitles
        number = 0
        subtitles_number = len(self.links_to_dl)
        self.rt.output('')
        self.rt.output(f'Downloading {subtitles_number} .zip files')
        self.rt.output('')
        for url in self.links_to_dl:                # lst containing urls with subtitles to download
            number += 1
            self.rt.output(f'{number}/{subtitles_number}', newline=False)
            save_path = cwd
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


class FileManager:
    rv = ReturnValues()
    rt = RedirectTerminal()

    def __init__(self, scene_group=rv.from_dir(use='scene_group'),        # returns the scene group e.g bar
                 name_group=rv.from_dir(use='name_group'),
                 rv=rv,
                 rt=rt):

        self.scene_group = scene_group
        self.name_group = name_group
        self.rv = rv
        self.rt = rt

    def extract_zip(self):
        dir_name = cwd
        ext = ".zip"

        for item in os.listdir(dir_name):               # loop through items in dir
            if item.endswith(ext):                      # check for ".zip" extension
                file_name = os.path.abspath(item)       # get full path of files
                zip_ref = zipfile.ZipFile(file_name)    # create zipfile object
                zip_ref.extractall(f'{dir_name}')       # extract file to dir
                zip_ref.close()                         # close file
                os.remove(file_name)                    # delete zipped file

    def rename_srt(self):       # rename best matching .srt file so MPC auto-loads it, places rest of the .srt-files in /subs directory
        rt.output('')
        subs = 'subs/'

        try:
            os.mkdir(subs)
        except FileExistsError:
            pass
        dir_name = cwd
        scene_group = self.scene_group
        preferred_ext = f'{scene_group}.srt'
        new_name = f'{self.name_group}.srt'
        ext = '.srt'
        try:
            for item in os.listdir(dir_name):       # preferr subtitles specifically for scene group over diffrent scene group
                if item.endswith(preferred_ext):
                    os.rename(item, new_name)
                    break
                elif item.endswith(ext) and 'HI' not in item:       # preferr non hearing impared subtitles
                    os.rename(item, new_name)
                    break
        except FileExistsError:
            pass
        finally:
            self.rt.output(f'Added ~/{self.name_group[0:8]}.../{new_name}')

        for item in os.listdir(dir_name):       # move .srt not matching above to ../subs
            if item.endswith(ext) and not item.startswith(new_name):
                shutil.move(item, f'subs/{item}')


cu = CurrentUser()
rt = RedirectTerminal()
wb = WebScraping()
fm = FileManager()


def rd_exit():
    rt.output('')
    rt.output('--- All done ---')
    rt.output('')


def no_match():
    rt.output('')
    rt.output(f'Nothing found for {wb.release_name} by {wb.scene_group}')
    rd_exit()


def not_valid():
    rt.output(f'Title: {wb.title} with release name {wb.release_name} by {wb.scene_group} is not valid')
    rt.output("Valid syntax is e.g 'foo.2021.1080p.WEB.H264-bar'")
    rd_exit()


def script():     # main, checks if user is admin, if registry context menu exists, search subscene for subtitles etc...
    rt.lbc_listbox()
    rt.output('Output:')
    rt.output('')
    while cu.got_file() is False:
        time.sleep(2)
        cu.got_file()
    if cu.is_admin():
        regkey.write_key()                              # regkey.reg gets written, adds a context menu option to start main.py when right clicking inside folder
        os.system('cmd /c "reg import regkey.reg"')     # imports regkey.reg to the registry
        rt.output('Registry key has been added')
        rt.output('New context menu avilable when right clicking inside a folder')
        return rd_exit()
    if cu.got_key() is False:                             # check if key exists
        # Re-run the program with admin rights
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)  # runs script as admin if not admin
    else:
        rt.output(f'Searching for titles matching {wb.title}')
        wb.search_title()
        if wb.title == wb.release_name or wb.title == wb.scene_group:
            return not_valid()
        urls_number = len(wb.search_title_lst)
        if urls_number == 1:
            rt.output(f"One exact match found for Title '{wb.title}' Released '{wb.year}'")
            rt.output('')
        elif urls_number == 0:
            return no_match()
        rt.output('')
        for x in range(urls_number):
            rt.output(f'Searching match {x+1}/{urls_number} for subtitles', newline=False)
            wb.search_for_subtitles(x)
            if len(wb.links_to_dl) > 1:
                rt.output(f"Subtitles found for '{wb.name_group}'")
                break
            if x > urls_number:
                return no_match()
        if len(wb.links_to_dl) == 0:
            return no_match()
        wb.download_zip()
        rt.output('')
        fm.extract_zip()
        fm.rename_srt()
        if len(wb.links_to_dl) >= 2:
            rt.output(f'Rest of the .srt-files moved to ~/{wb.name_group[0:8]}.../subs\n')
        rt.output('')
        rd_exit()


if __name__ == "__main__":
    root = tk.Tk()
    Gui(root)
    root.mainloop()
