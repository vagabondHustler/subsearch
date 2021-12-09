## Subscene search

<p>Download subtitles for well known scene groups with two easy mouse clicks inside a directory. The subtitles are grabbed from Subscene.com.
<p>There are probably better repositories out there than this one, that does the same thing, I made this one mainly to learn python and git by doing.

---

#### TODO:

- [x] Remove GUI
- [x] Improve search times
- [x] Let user pick subtitle languish trough terminal
- [ ] Look into some sort of terminal menu system
- [ ] Find a better way to run script than trough cmd
- [ ] Add opensubtitles as a source for subs
- [ ] Improve code?
- [ ] Learn HTML so I write better .md files ^\_^

---

### Supported languages:

These are the fully supported languages, but all languages [subscene](https://u.subscene.com/filter) offers as a filter will work, but searches for TV-shows might be slower, more results to filter trough.

- Arabic,`ar`
- Brazillian Portuguese, `pt_BR`
- Danish, `dk`
- Dutch, `nl`
- English, `en`
- Finnish, `fi`
- French, `fr`
- German, `de`
- Hebrew, `he`
- Indonesian, `id`
- Italian, `it`
- Korean, `ko`
- Norwegian, `no`
- Romanian, `ro`
- Spanish, `es`
- Swedish, `sv`
- Thai, `th`
- Turkish, `tr`
- Vietnamese, `vi`

### How to use:

1. Run `python main.py` to add the context-menu.

   1. You will be prompted to run as admin, necessary to save the new keys to the registry.
   2. You will be asked to proived the language you want the subtitles to be in.
   3. Context menu gets added and you can now Right-Clicking inside a folder to see context-menu option 'Search subscene'.

2. Use the menu inside the folder of the release you want to find subtitles for.
   1. If there are any problems it will be displayed in `cwd/subscene-search.log`

#### Misc:

Registry key can be found here: `Computer\HKEY_CLASSES_ROOT\Directory\Background\shell\Search subscene`

If you don't want the icon in the context menu, delete Name: `Icon` Type: `REG_SZ` in Key: `Search subscene`

You can change the subtitle language in `config/language.txt`

If u're running VS Code and are getting decode, encode errors add in settings.json:
     ```"code-runner.executorMap": {
    "python": "set PYTHONIOENCODING=utf8 && python"
  },```
   
