<h1 align="center"><img src="https://raw.githubusercontent.com/vagabondHustler/SubSearch/main/assets/subsearch_v2.png"/></h1>

<div align="center">
  
![Status](https://img.shields.io/badge/status-active-success?&style=flat-square&labelColor=1e1e2e&color=a6e3a1)
![Version](https://img.shields.io/github/v/tag/vagabondhustler/subsearch?style=flat-square&labelColor=1e1e2e&color=eba0ac)
![Downloads](https://img.shields.io/github/downloads/vagabondhustler/subsearch/total?style=flat-square&labelColor=1e1e2e&color=f5c2e7)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/vagabondhustler/subsearch?&style=flat-square&labelColor=1e1e2e&color=fab387)
![License](https://img.shields.io/github/license/vagabondhustler/SUbSearch?&style=flat-square&labelColor=1e1e2e&color=b4befe)

</div>

#### Readme Table of Contents

- [About](#about)
- [Preview](#preview)
- [PyPi](#pypi)
- [Source](#src)
- [MSI Installer](#msi)
- [Acknowledgements](#thanks)

#### Wiki Table of Contents

- [Home](https://github.com/vagabondHustler/subsearch/wiki)
- [Code Analysis and Verification Process](https://github.com/vagabondHustler/subsearch/wiki/Code-Analysis-and-Verification-Process)
- [Fixing Context Menu Issue in Subsearch](https://github.com/vagabondHustler/subsearch/wiki/Fixing-Context-Menu-Issue-in-Subsearch)
- [GUI-Options](https://github.com/vagabondHustler/subsearch/wiki/GUI-Options)
- [Troubleshooting Subtitle Search Issues](https://github.com/vagabondHustler/subsearch/wiki/Troubleshooting-Subtitle-Search-Issues)

#### Misc Table of Contents

- [Contributing](https://github.com/vagabondHustler/SubSearch/blob/main/.github/CONTRIBUTING.md)
- [Reporting a Vulnerability](https://github.com/vagabondHustler/SubSearch/blob/main/.github/SECURITY.md)

## About <a name = "about"></a>

#### Key Features
  
- Initiate a search for subtitles by simply right-clicking on a media file.
- Search for subtitles in 70 different languages
- Some of the subtitle filters are HI, non-HI, foreign parts only.
- User-friendly GUI for easy customization and configuration
- Available as a compiled executable, source code via GitHub and PyPI
- The setup process is straightforward.

#### Details

Subsearch is an automated subtitle downloader and extractor that allows users to search and download subtitles for movies and TV shows with a single click from the context menu. The application features a graphical user interface for configuring settings, including options for searching subtitles in 70 different languages from various subtitle sites, filtering hearing-impaired subtitles, and adjusting filename matching criteria.

The application has a user-friendly GUI for all custom settings that can be easily configured. It supports 70 different languages, most of which work on all available subtitle sites. Users can configure it to include hearing impaired subtitles only, non-hearing impaired subtitles only, or both. They can also adjust how strictly the file name matches the search results.

Initially created as a personal project to learn Python programming and git version control, this application has evolved into a daily-use tool that I continue to enjoy working on. While there are many similar repositories available that automatically download subtitles from the internet, this project may offer unique features that set it apart. The setup process has been designed to be as straightforward as possible with minimal reliance on external modules.

## Preview <a name = "preview"></a>

<div align="center">

![prtsc_example](https://raw.githubusercontent.com/vagabondHustler/SubSearch/main/assets/example.gif)

<details>
<summary>Screenshots of the interface</summary>

![prtsc_language](https://github.com/vagabondHustler/subsearch/blob/main/assets/language_options.png?raw=true)

![prtsc_search](https://github.com/vagabondHustler/subsearch/blob/main/assets/search_filters.png?raw=true)

![prtsc_settings](https://github.com/vagabondHustler/subsearch/blob/main/assets/subsearch_options.png?raw=true)

![prtsc_download](https://github.com/vagabondHustler/subsearch/blob/main/assets/download_manager.png?raw=true)

</details>

</div>

## Getting Started <a name = "getting_started_src"></a>

#### PyPi<a name = "pypi"></a>

- Download Python version 3.10 or later.
- Install Subsearch by running `pip install subsearch` in the command prompt.
- Launch the app by running `subsearch`.

#### Source code <a name = "src"></a>

- Download and install Python version 3.10 or later.
- Clone the Subsearch repository by running `git clone https://github.com/vagabondHustler/subsearch.git`.
- Install Subsearch by running `pip install -e <local project path>[package-index-options]`. For example, run `pip install -e .` for only required dependencies or `pip install -e .[dev, optional]` for dev/optional dependencies.
- Build the executable and MSI installer by running `python setup.py bdist_msi`.

#### Subsearch .msi Installer <a name = "msi"></a>

- Download `SubSearch-x.x.x-win64.msi` from the Subsearch releases [page](https://github.com/vagabondHustler/SubSearch/releases)
- Install the .msi file.
- Run Subsearch.exe at least once
- To update from a previous version, download and run the new installer in the same directory. If installed in a different directory, delete the old registry key (see Wiki for details).the same directory. Else you might have to delete the old registry key, (see [Wiki](https://github.com/vagabondHustler/subsearch/wiki/Fixing-Context-Menu-Issue-in-Subsearch) for details).
- If you receive a PUA message, click `More info`.

<details>
<summary>Screenshots of PUA message<a name = "code"></a></summary>

![prtsc_moreinfo](https://raw.githubusercontent.com/vagabondHustler/SubSearch/main/assets/moreinfo.png)

![prtsc_runanyway](https://raw.githubusercontent.com/vagabondHustler/SubSearch/main/assets/runanyway.png)

---

</details>

## Acknowledgements<a name = "thanks"></a>

I would like to express my gratitude to the following repositories for providing templates, scripts, inspiration, themes, and solutions to similar problems:

- [othneildrew/Best-README-Template](https://github.com/othneildrew/Best-README-Template)
- [pimoroni/template-python](https://github.com/pimoroni/template-python/blob/master/.github/CONTRIBUTING.md)
- [manojmj92/subtitle-downloader](https://github.com/manojmj92/subtitle-downloader)
- [psf/black](https://github.com/psf/black)
- [zavoloklom/material-design-iconic-font](https://github.com/zavoloklom/material-design-iconic-font) // icons
- [rdbende/Sun-Valley-ttk-theme](https://github.com/rdbende/Sun-Valley-ttk-theme) // base theme
- [siddheshsathe/handy-decorators](https://github.com/siddheshsathe/handy-decorators)
- [TransparentLC](https://github.com/TransparentLC) // spritesheet_generator.js
