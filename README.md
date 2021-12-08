# subscene-search

Download subtitles for well known scene groups with two easy mouse clicks inside a directory on Windows. The subtitles are grabbed from Subscene.com

### Supported languages

These are the fully supported languages, but all languages [subscene](https://u.subscene.com/filter) offers as a filter will work, but search might be slower.

- Arabic,`ar`
- Brazillian Portuguesed, `pt_BR`
- Danishd, `dk`
- Dutchd, `nl`
- Englishd, `en`
- Finnishd, `fi`
- Frenchd, `fr`
- Germand, `de`
- Hebrewd, `he`
- Indonesiand, `id`
- Italiand, `it`
- Koreand, `ko`
- Norwegiand, `no`
- Romaniand, `ro`
- Spanishd, `es`
- Swedishd, `sv`
- Thaid, `th`
- Turkishd, `tr`
- Vietnamesed, `vi`

### How to use:

1. Run `python main.py` to add the context-menu.
   1. You will be prompted to run as admin, necessary to save the new keys to the registry.
   2. You will be asked to proived the language you want the subtitles to be in.
   3. Context menu gets added and you can now Right-Clicking inside a folder to see context-menu option 'Search subscene'.

2. Use the menu inside the folder of the release you want to find subtitles for.
   1. You can change the subtitle language in config/language.txt

### Misc

Registry key can be found here:`Computer\HKEY_CLASSES_ROOT\Directory\Background\shell\Search subscene` if you want to remove it or make edits to it.

<p>

If you don't want the icon in the context menu, delete Name:`Icon` Type: `REG_SZ` in Key: `Search subscene`
