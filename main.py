import requests                  # HTTP libary to easily send requests
import webbrowser                # open website URL in deafult browser
from bs4 import BeautifulSoup    # pulling data out of HTML/XML files
import os


'''
    The standard for naming a scene release is typically by Title.Year.Soruce.Codec-GroupName, e.g foo.2021.1080p.WEB.H264-bar
    This standard can be used to filter everything but Title and Year and use it as str to search with
    The str can be aquired from selecting the scene release directory
'''


def select_release_dir():
    dir_name = os.getcwd()
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


def releases_menu(release_name: str):                  # scraped information gets combined title of the movie and link to subtitles
    menu_dict = {}
    for number, item in enumerate(search_subscene(release_name)):   # enumerate so the number can be used to select key in dict
        number += 1
        if number < 10:                                             # formatting reasons
            print(number, item[0])                                  # prints out lst with number before title, e.g 1 foo (2021)
            menu_dict[number] = item[1]                             # create key for dict, with key: number, value: link
        else:
            print(number, item[0])
            menu_dict[number] = item[1]
    print('\n')
    while True:
        menu_item = input('\nInput number to open URL or exit: ')
        try:
            int(menu_item)
            if len(str(menu_item)) == 0:
                print('Not a valid option')
                continue
            if int(menu_item) > int(number):
                print(f'You typed {menu_item} but only {number} numbers exists as a option\n')
                continue
            else:
                break
        except ValueError as err:
            if menu_item == 'exit':
                exit(f'Exit, user input {menu_item}')
            print(f'Not a valid option\nError: {err}\n')
            continue

    for key, value in menu_dict.items():                            # unpack key and values
        if int(menu_item) == key:                                   # if user input matches key
            webbrowser.open(value)                                  # opens value of selected key in the webroser


def search_subscene(name_of_release: str, a_dict=[]):
    elements = scraping_subscene(search_parameters(name_of_release), 'left', 'div', 'title')    # name_of_release='foo 2021', find_id='left', find_type='div', find_class='title'
    media_lst = title_lst_appender(elements)  # lst ('title of release', 'link to subtitles')
    return media_lst


def search_parameters(the_title: str):
    search_url = f'https://subscene.com/subtitles/searchbytitle?query={the_title}'      # 'foo 2021'
    return search_url                                                                   # https://subscene.com/subtitles/searchbytitle?query=foo%202021


def scraping_subscene(name_of_release=None, find_id=None, find_type=None, find_class=None):         # 'foo 2021', 'left', 'div', 'title'
    search_results = requests.get(name_of_release)

    title_soup = BeautifulSoup(search_results.content, 'html.parser')
    results = title_soup.find(id=find_id)

    elements = results.find_all(find_type, class_=find_class)
    return elements


def title_lst_appender(elements, lst=[]):               # removes unnecessary HTML code
    for element in elements:
        links = element.find_all()                      # name of the title with HTML code and URL to subtitles
        link_soup = str(links)[0:-5:].split('>')        # remove unnecessary HTML code
        name = link_soup[1]                             # name of the title
        for link in links:                              # append all links into a list
            link_url = link['href']
            link = (name, 'https://subscene.com'+(f'{link_url}'))   # tuple (name, URL), e.g ('foo 2021', 'https://subscene.com/subtitles/foo-2021')
            lst.append(link)
    return lst


release_name = title_filter()
releases_menu(release_name)
# a = input('> ')
# print_list(a)
