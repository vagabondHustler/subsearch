# subscene_search
Download subtitles from subscene.com with the name of a directory as the search parameter from the context menu.

<p>This branch has a few, but everything is automatic from the search to the downloading and unzipping of the .srt-files.
<p>The main branch has no requirements besides python3.10, but only opens the initial search result in the webbrowser.

---


- The standard for naming a scene release is typically by Title.Year.Soruce.Codec-GroupName, e.g foo.2021.1080p.WEB.H264-bar
- This standard can be used as a search parameter, we only need to fetch the path and directory name, then remove everything but the Title


---

# How to use:
1. Run ```python main.py``` from where you are planning to store it
2. Context menu gets added when Right-Clicking inside a folder, named 'Search subscene'
3. Use the menu insde the folder you want to use as a search parameter
4. Registry key can be found here:```Computer\HKEY_CLASSES_ROOT\Directory\Background\shell\Search subscene```
