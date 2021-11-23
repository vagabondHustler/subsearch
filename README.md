# subscene_search
Download subtitles for well known scene groups with two easy mouse clicks inside a directory on Windows. The subtitles are grabbed from Subscene.com

<p>This branch has a few dependencies, but everything is automatic from the search to the downloading and unzipping of the .srt-files.
<p>The main_no-dependencies branch has no requirements besides python3.10, but only opens the initial search result in the webbrowser.

---


- The standard for naming a scene release is typically by Title.Year.Soruce.Codec-GroupName, e.g foo.2021.1080p.WEB.H264-bar
- This standard can be used as a search parameter, we only need to fetch the path and directory name, then remove everything but the Title


---

# How to use:
1. Run ```python main.py``` to add the context-menu.
	1. You will be prompted to run as admin, nessecarry to save the new keys to the registry.
	2. Context menu gets added and you can now Right-Clicking inside a  folder to see context-menu option 'Search subscene'.

2. Use the menu inside the folder of the release you want to find subtitles for.
  1. Most settings, like language can be tweaked in class ```WebScraping:``` method ```__init__``` in ```main.py```

---  
Registry key can be found here:```Computer\HKEY_CLASSES_ROOT\Directory\Background\shell\Search subscene``` if you want to remove it or make edits to it.

<p>

If you don't want the icon in the context menu, delete Name:```Icon``` Type: ```REG_SZ``` in Key: ```Search subscene```
