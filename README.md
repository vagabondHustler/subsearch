# subscene_downloader
Download subtitles from subscene.com with the name of a directory as the search parameter

# How to:
1. Start regedit ```WIN+R``` ```regedit```
2. Go to ```Computer\HKEY_CLASSES_ROOT\Directory\Background\shell\```
3. Create new key named whatever you want your context menu text to be
4. Create new key inside ```Computer\HKEY_CLASSES_ROOT\Directory\Background\shell\Subscene_downloader``` named ```command```
5. Modify default ```cmd.exe "%V" /c  python path_to_project\subscene_downloader\main.py```
6. Install dependencies:
```pip install -r docs/requirements.txt```

![alt text](https://github.com/vagabondHustler/subscene_downloader/blob/context-menu/resources/prtsc.png)

# ToDoList
- ~~simple terminal menu~~
- ~~search with folder name~~
- ~~add to context menu~~
- ~~Run from context menu in cwd~~
- Auto add registry key/context menu
- Add gui
