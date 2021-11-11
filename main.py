import requests                  # HTTP libary to easily send requests
import webbrowser                # open website URL in deafult browser
from bs4 import BeautifulSoup    # pulling data out of HTML/XML files
from tkinter import filedialog   # folder dialog


'''
    The standard for naming a scene release is typically by Title.Year.Soruce.Codec-GroupName, e.g foo.2021.1080p.WEB.H264-bar
    This standard can be used to filter everything but Title and Year and use it as str to search with
    The str can be aquired from selecting the scene release directory
'''


def select_release_dir():
    dir_name = filedialog.askdirectory(initialdir='/', title='Select release directory')     # directory prompt
    if dir_name == '':
        exit('Exit. No directory selected')
    else:
        return dir_name     # return the value, used in title_filter


def title_filter(release_title_lst=[]):
    dir_name = select_release_dir()                     # directory prompt, e.g: C:/Users/username/Downloads/foo.2021.1080p.WEB.H264-bar
    dir_name_lst = dir_name.split('/')                  # removes / form the path to the directry e.g: 'C:' 'Users' 'username' 'Downloads' 'foo.2021.1080p.WEB.H264-bar'
    release_dot_name = dir_name_lst[-1]                 # get last part of the path which is the release name with . as spaces e.g: foo.2021.1080p.WEB.H264-bar
    release_name_lst = release_dot_name.split('.')      # remove the . from the release name e.g: 'foo' '2021' '1080p' 'WEB' 'H264-bar'
    for word in release_name_lst:                       # loop through lst
        try:                                            # if word is not a int ValueError is raised
            int(word)
            release_title_lst.append(word)              # if word is a Year it gets append to lst
            break                                       # breaks the for loop and leaves the rest of the release name
        except ValueError:
            release_title_lst.append(word)              # appends the Title to from the release name
    name_of_release = ' '.join(release_title_lst)       # join the lst into str with spaces between words
    return name_of_release                              # returns name of release with year eg 'foo 2021'


