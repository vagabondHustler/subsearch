# Subscene scraper
Download subtitles from subscene.com with the name of a directory as the search parameter from the context menu.


---

- The standard for naming a scene release is typically by Title.Year.Soruce.Codec-GroupName, e.g foo.2021.1080p.WEB.H264-bar
- This standard can be used to filter everything but Title and Year and use it as str to search with
- The str can be acquired from selecting the scene release directory

---
# How to add context menu:
1. Start regedit ```WIN+R``` ```regedit```
2. Go to ```Computer\HKEY_CLASSES_ROOT\Directory\Background\shell\```
3. Create new key named whatever you want your context menu text to be, I named it ```Search subscene```
4. If you want a icon, 'New > String Value', name it Icon, value ```path_to_icon\icon.ico, 0``` 0 for first obj, 1 for second etc, etc
5. Create 'New > Key' inside ```Computer\HKEY_CLASSES_ROOT\Directory\Background\shell\Search subscene ``` named ```command```
6. Modify 'default' ```cmd.exe "%V" /c  python path_to_project\subscene_downloader\main.py```
~~7. Install dependencies:~~
~~```pip install -r docs/requirements.txt```~~

# ToDoList
- ~~simple terminal menu~~
- ~~search with folder name~~
- ~~add to context menu~~
- ~~Run from context menu in cwd~~
- Auto add registry key/context menu with module winreg
- compile a exe so no dependencies/python is requierd
