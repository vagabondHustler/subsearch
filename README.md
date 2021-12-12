<h1 align="center">Subscene search</h3>


<div align="center">
    
##### prtsc of Terminal output if it's not hidden
    
![prtsc](https://github.com/vagabondHustler/subscene-search/blob/main/assets/prtsc.png)
    
</div>

<div align="center">
Download subtitles for well known scene groups with two easy mouse clicks inside a directory

---
    
<p>
    
[![Status](https://img.shields.io/badge/status-active-success.svg)]()
![GitHub commit activity](https://img.shields.io/github/commit-activity/w/vagabondHustler/subscene-search)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](/LICENSE)
    
</div>

## Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [Usage](#usage)
- [Language support](#lsupport)
- [TODO](https://github.com/vagabondHustler/subscene-search/blob/main/TODO.md)
- [Authors](#authors)
- [Misc](#misc)

## About <a name = "about"></a>
Made mainly to learn python and git, by doing. There are probably better repositories out there that grab subtitles automatically from the web. But feel free to check this one out if you want to. The avragee run time is around 1 second, a little bit longer for TV-shows due to the high amount of titles, season eppisode to go trough, but not by much if you are searching with a [supported](#lsupport) language.

## Getting Started <a name = "getting_started"></a>

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

```
Python 3.10
```

### Installing

#### Clone the project
```
git clone https://github.com/vagabondHustler/subscene-search
```
#### Install dependencies
```
pip install -r path/subscene-search/docs/requirements.txt
```
#### Run main
```
python main.py 
```

## Usage <a name="usage"></a>

After everything is setup, you should be able to fetch subtitles by right clicking inside a directory containng the movie/Tv-show, keep in mind the directory needs to have the standard release format.
```
Title.Year.Soruce.Codec-GroupName, e.g foo.2021.1080p.WEB.H264-bar
```
For easy configuration of language, toggle context menu icon and similar features, run.
```
python configure.py 
```
If you for some reason don't wanna use pwsh.exe to run python, rename `/src/cmd_regkey.py` to `regkey.py`, and del/rename the current one.

I dont think Windows comes with `C:\Program Files\PowerShell\7\pwsh.exe` by deafult but powershell.exe does? On line 12 in `/src/regkey.py`, replace `pwsh.exe` with `powershell.exe` or use `/src/cmd_regkey.py` as mentioned above.

## Supported languages <a name = "lsupport"></a>

These are the fully supported languages, but all languages [subscene](https://u.subscene.com/filter) offers as a filter will work, but searches for TV-shows might be slower, more results to filter trough.

- Arabic, `ar`
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

## Authors <a name = "authors"></a>

- [@vagabondHustler](https://github.com/vagabondHustler)

## Misc <a name = "misc"></a>

Registry key can be found here: `Computer\HKEY_CLASSES_ROOT\Directory\Background\shell\Search subscene`

If you don't want the icon in the context menu, delete Name: `Icon` Type: `REG_SZ` in Key: `Search subscene`
