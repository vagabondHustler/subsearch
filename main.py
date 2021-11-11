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


