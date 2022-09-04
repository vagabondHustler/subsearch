<h1 align="center"><img src="https://raw.githubusercontent.com/vagabondHustler/SubSearch/main/assets/subsearch_v2.png"/></h1>

<div align="center">

![Status](https://img.shields.io/badge/status-active-success?color=9fa65d&style=flat-square)
![Tests](https://img.shields.io/github/workflow/status/vagabondhustler/subsearch/Tests/main?color=9fa65d&label=tests&style=flat-square)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/vagabondhustler/subsearch?color=c49b5d&style=flat-square)
![Version](https://img.shields.io/github/v/release/vagabondHustler/SubSearch?color=de935e&display_name=tag&include_prereleases&style=flat-square)
![Downloads](https://img.shields.io/github/downloads/vagabondHustler/SubSearch/total?color=ba9888&style=flat-square)
![License](https://img.shields.io/github/license/vagabondhustler/SUbSearch?color=82a2bd&style=flat-square)

</div>

## Table of Contents

- [About](#about)
- [Getting Started](#getting_started_src)
- [Preview](#preview)
- [PyPi](#pypi)
- [Source](#src)
- [Executable](#exe)
- [Supported Languages](#lsupport)
- [Authors](#authors)
- [Contributing](https://github.com/vagabondHustler/SubSearch/blob/main/.github/CONTRIBUTING.md)
- [Reporting a Vulnerability](https://github.com/vagabondHustler/SubSearch/blob/main/.github/SECURITY.md)
- [Special Thanks](#thanks)

## About <a name = "about"></a>

- Automatically search, download and extract subtitles for any movie or show with one easy mouse click from the context menu.
- Has a GUI for all the custom settings that can be configured.
- For 70 different languages, of which most work on all available subtitle sites.
- Can be configured to include hearing impaired subtitles only, none-hearing impaired subtitles only or both.
- Configure how strictly the file name has to match the search results.
- Can be ran from a compiled executable, without the need for a Python interpreter and importing modules.
- Subtitles are gathered from subscene and opensubtitles.
- Pick where you get the subtitles from.
- Works inside and outside of a env.

This started as a fun project to learn how to code in python and how to use git, has now developed into a application I use daily and enjoy working on. There are many similar repositories out there that grab subtitles automatically from the web, so this might not be the most unique project. But feel free to check this one out, might offer something new. Have tried to make the setup processes as painless as possible with the use of as few external modules as possible. The average run time is around 1 second, a little bit longer for TV-Series due to the high amount of titles.

Feel free to ask me anything about this project, request new features, contribute or give constructive feedback.

## Preview <a name = "preview"></a>

<div align="center">

While searching for subs if show terminal is disabled

![prtsc_example](https://raw.githubusercontent.com/vagabondHustler/SubSearch/main/assets/example_21224.gif)

Available options in the widget

![prtsc_language](https://raw.githubusercontent.com/vagabondHustler/subsearch/main/assets/gui_language_22054.png)

![prtsc_search](https://raw.githubusercontent.com/vagabondHustler/subsearch/main/assets/gui_search_22054.png)

![prtsc_settings](https://raw.githubusercontent.com/vagabondHustler/subsearch/main/assets/gui_settings_22054.png)

![prtsc_download](https://raw.githubusercontent.com/vagabondHustler/SubSearch/main/assets/gui_download_22054.png)

</div>

## Getting Started <a name = "getting_started_src"></a>

Source is probably faster than the executable version, but the executable can be run without installing a Python interpreter or any modules.

### PyPi <a name = "pypi"></a>

Download [Python](https://www.python.org/downloads/) >= 3.10

Install subsearch

`pip install subsearch`

Add the context-menu

`subsearch --registry-key add`

More options

`subsearch --help`

See [code block](#code) for imports

### Source <a name = "src"></a>

Download [Python](https://www.python.org/downloads/) >= 3.10

Download subsearch

`git clone https://github.com/vagabondHustler/subsearch.git`

Install package locally

`pip install -e .`

Code <a name = "code"></a>

```
from subsearch import Subsearch
from subsearch.utils.raw_config import get_config, set_config


def main() -> None:
    config = get_config()
    config["providers"]["opensubtitles_hash"] = False
    set_config(config)
    ss = Subsearch()
    ss.subscene_scrape()
    ss.opensubtitles_scrape()
    ss.process_files()
    ss.end()


if __name__ == "__main__":
    main()
```

`python -m main c:\users\vagabondhustler\desktop\foo.bar.the.movie.2022.1080p-foobar.mkv`

### Executable <a name = "exe"></a>

Download SubSearch-vx.x.x-win-x64.zip from releases - [Download URL](https://github.com/vagabondHustler/SubSearch/releases)

Unzip file and run SubSearch.exe

If you get a PUA message, click `More info`

![prtsc_moreinfo](https://raw.githubusercontent.com/vagabondHustler/SubSearch/main/assets/moreinfo.png)

![prtsc_runanyway](https://raw.githubusercontent.com/vagabondHustler/SubSearch/main/assets/runanyway.png)

If no subtitles are found or no subtitles (including the folder subs with extra .srt files) are synced with the movie check the **subsearch**.log for a list with download links to all the different subtitles that didn't pass the search threshold percentage or decrease the value in the settings GUI, accessed from SubSearch.exe

## Supported languages <a name = "lsupport"></a>

`N/A` = not supported on opensubtitles

`Albanian alb` `Arabic ara` `Armenian arm` `Azerbaijani aze` `Basque baq` `Belarusian bel` `Bosnian bos` `Brazillian-Portuguese pob` `Bulgarian bul` `Bulgarian-English N/A` `Burmese bur` `Cambodian-Khmer khm` `Catalan cat` `Chinese-BG-code zht` `Croatian hrv` `Czech cze` `Danish dan` `Dutch dut` `Dutch-English N/A` `English eng` `English-German N/A` `Esperanto epo` `Estonian est` `Finnish fin` `French fre` `Georgian geo` `German ger` `Greenlandic N/A` `Hebrew heb` `Hindi hin` `Hungarian hun` `Hungarian-English N/A` `Icelandic ice` `Indonesian ind` `Italian ita` `Japanese jpn` `Kannada kan` `Kinyarwanda N/A` `Korean kor` `Kurdish kur` `Latvian lav` `Lithuanian lit` `Macedonian mac` `Malayalam mal` `Manipuri mni` `Mongolian mon` `Nepali nep` `Norwegian nor` `Pashto N/A` `Punjabi N/A` `Romanian rum` `Russian rus` `Serbian scc` `Sinhala sin` `Slovak slo` `Slovenian slv` `Somali som` `Spanish spa` `Sundanese sun` `Swahili swa` `Swedish swe` `Tagalog tgl` `Tamil tam` `Telugu tel` `Thai tha` `Turkish tur` `Ukrainian ukr` `Urdu urd` `Vietnamese vie` `Yoruba N/A`

## Authors <a name = "authors"></a>

- [@vagabondHustler](https://github.com/vagabondHustler)

## Special Thanks<a name = "thanks"></a>

- To the people at [othneildrew/Best-README-Template](https://github.com/othneildrew/Best-README-Template) for `README` template
- To the people at [pimoroni/template-python](https://github.com/pimoroni/template-python/blob/master/.github/CONTRIBUTING.md) for `CONTRIBUTING` template
- To the people at [manojmj92/subtitle-downloader](https://github.com/manojmj92/subtitle-downloader) for inspiration, ways of solving similar problems
- To the people at [psf/black](https://github.com/psf/black) for ways of doing workflow related tasks
- To the people at [zavoloklom/material-design-iconic-font](https://github.com/zavoloklom/material-design-iconic-font) for amazing icons
