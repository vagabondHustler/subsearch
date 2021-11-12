import webbrowser       # open website URL in deafult browser
import os               # get cwd
import regkey           # .py file to write regkey.reg, easier than doing through winreg
import ctypes           # run as admin
import sys              # execute main.py
import winreg as reg    # check if sub keys allready exists

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
        webbrowser.open(url)                                        # returns name of release with year eg 'foo'


Search.subscene(Search.parameter(current_working_dir()))
