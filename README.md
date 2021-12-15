<div align="center">
    
# Subscene search

![prtsc](https://github.com/vagabondHustler/subscene-search/blob/main/assets/prtsc.png)

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

Download subtitles for movies and tv-series, automatically for well known scene groups with two easy mouse clicks inside the directory containing the video file, if there is no video file inside the directory, the directory name will be used as a search parameter.

This can be useful if the video file is comppressed inside a rar/zip archive or if the video file is of a unusual extension type not implement in the code.

Made mainly to learn python and git, by doing. There are probably better repositories out there that grab subtitles automatically from the web. But feel free to check this one out if you want to. The avragee run time is around 1 second, a little bit longer for TV-Series due to the high amount of titles, season eppisode to go trough, but not by much if you are searching with a [supported](#lsupport) language.

## Getting Started <a name = "getting_started"></a>

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

<sup>Everything works to be ran from a venv, just have it active first time running main.py. If you dont want it enable/disable at a later time, just run configure.py with the venv active/deactivated and do menu option 3. "Show Terminal on search", and the python.exe/pythonw path will update, just be sure to have the dependencies installed.<sup>

```
pip install -r path/subscene-search/docs/requirements.txt
```

#### Run main

```
python main.py
```

#### Run configure (Optinal)

<sup>Configure language, toggle context-menu icon, show terminal True/False and more.</sup>

```
python configure.py
```

## Usage <a name="usage"></a>

After everything is setup, you should be able to fetch subtitles by right clicking inside a directory containng the movie/TV-Series, keep in mind the directory/video-file needs to have the standard release format.

```
Title.Year.Soruce.Codec-GroupName, e.g foo.2021.1080p.WEB.H264-bar
```

For easy configuration of language, toggle context menu icon and similar features, run.

## Supported languages <a name = "lsupport"></a>

These are the fully supported languages, but all languages [subscene](https://u.subscene.com/filter) offers as a filter will work, but searches for TV-Series might be slower, more results to filter trough.

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
