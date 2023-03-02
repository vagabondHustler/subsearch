<h1 align="center"><img src="https://raw.githubusercontent.com/vagabondHustler/SubSearch/main/assets/subsearch_v2.png"/></h1>

<div align="center">

![Status](https://img.shields.io/badge/status-active-success?&style=flat-square)
![Tests](https://img.shields.io/github/actions/workflow/status/vagabondhustler/subsearch/tests.yml?branch=main&label=tests&style=flat-square)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/vagabondhustler/subsearch?&style=flat-square)
![Version](https://img.shields.io/github/v/release/vagabondHustler/SubSearch?&display_name=tag&include_prereleases&style=flat-square)
![Dls_total](https://img.shields.io/github/downloads/vagabondhustler/subsearch/total?label=downloads%40total&style=flat-square)
![Dls_latest](https://img.shields.io/github/downloads/vagabondhustler/subsearch/latest/total?style=flat-square)
![License](https://img.shields.io/github/license/vagabondhustler/SUbSearch?&style=flat-square)

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
- [Subsearch Settings](https://github.com/vagabondHustler/subsearch/wiki/Subsearch-Settings)
- [Troubleshooting Subtitle Search Issues](https://github.com/vagabondHustler/subsearch/wiki/Troubleshooting-Subtitle-Search-Issues)

#### Misc Table of Contents

- [Contributing](https://github.com/vagabondHustler/SubSearch/blob/main/.github/CONTRIBUTING.md)
- [Reporting a Vulnerability](https://github.com/vagabondHustler/SubSearch/blob/main/.github/SECURITY.md)

## About <a name = "about"></a>

#### Key Features
  
  - Initiate a search for subtitles by simply right-clicking on a media file.
  - Search for subtitles in 70 different languages
  - User-friendly GUI for easy customization and configuration
  - Available in three options, including a compiled executable and source code on GitHub and PyPI
  - The setup process is straightforward and has minimal reliance on external modules.

#### Details 

Subsearch is an automated subtitle downloader and extractor that allows users to search and download subtitles for movies and TV shows with a single click from the context menu. The application features a graphical user interface for configuring settings, including options for searching subtitles in 70 different languages from various subtitle sites, filtering hearing-impaired subtitles, and adjusting filename matching criteria.

The application has a user-friendly GUI for all custom settings that can be easily configured. It supports 70 different languages, most of which work on all available subtitle sites. Users can configure it to include hearing impaired subtitles only, non-hearing impaired subtitles only, or both. They can also adjust how strictly the file name matches the search results.

The tool is available in three different options: as a compiled executable that can be run without the need for a Python interpreter and imported modules, as source code on GitHub, and on PyPI. Users can pick the source that suits them best.

Initially created as a personal project to learn Python programming and git version control, this application has evolved into a daily-use tool that I continue to enjoy working on. While there are many similar repositories available that automatically download subtitles from the internet, this project may offer unique features that set it apart. The setup process has been designed to be as straightforward as possible with minimal reliance on external modules. 


## Preview <a name = "preview"></a>

<div align="center">

![prtsc_example](https://raw.githubusercontent.com/vagabondHustler/SubSearch/main/assets/example.gif)

<details>
<summary>Screenshots of the interface</summary>

![prtsc_language](https://raw.githubusercontent.com/vagabondHustler/subsearch/main/assets/gui_language.png)

![prtsc_search](https://raw.githubusercontent.com/vagabondHustler/subsearch/main/assets/gui_search.png)

![prtsc_settings](https://raw.githubusercontent.com/vagabondHustler/subsearch/main/assets/gui_settings.png)

![prtsc_download](https://raw.githubusercontent.com/vagabondHustler/SubSearch/main/assets/gui_download.png)

</details>

</div>

## Getting Started <a name = "getting_started_src"></a>

#### PyPi<a name = "pypi"></a>

- Download Python version 3.10 or later.
- Install Subsearch by running `pip install subsearch` in the command prompt.
- Add the context menu by running `subsearch --registry-key add`.
- For additional options, run `subsearch --help` in the command prompt.

#### Source code <a name = "src"></a>

- Download and install Python version 3.10 or later.
- Clone the Subsearch repository by running `git clone https://github.com/vagabondHustler/subsearch.git`.
- Install Subsearch by running `pip install -e <local project path>[package-index-options]`. For example, run `pip install -e .` for only required dependencies or `pip install -e .[dev, optional]` for dev/optional dependencies.
- Build the executable and MSI installer by running `python setup.py bdist_msi`.

#### Subsearch .msi Installer <a name = "msi"></a>

- Download `SubSearch-x.x.x-win64.msi` from the Subsearch releases [page](https://github.com/vagabondHustler/SubSearch/releases)
- Install the .msi file.
- To update from a previous version, download and run the new installer in the same directory. If installed in a different directory, delete the old registry key (see Wiki for details).the same directory. Else you might have to delete the old registry key, (see [Wiki](https://github.com/vagabondHustler/subsearch/wiki/Fixing-Context-Menu-Issue-in-Subsearch) for details).
- If you receive a PUA message, click `More info`.

<details>
<summary>Screenshots of PUA message<a name = "code"></a></summary>

![prtsc_moreinfo](https://raw.githubusercontent.com/vagabondHustler/SubSearch/main/assets/moreinfo.png)

![prtsc_runanyway](https://raw.githubusercontent.com/vagabondHustler/SubSearch/main/assets/runanyway.png)

---

</details>

## Acknowledgements<a name = "thanks"></a>

I would like to express my gratitude to the following repositories for providing templates, inspiration, themes, and solutions to similar problems:

- [othneildrew/Best-README-Template](https://github.com/othneildrew/Best-README-Template)
- [pimoroni/template-python](https://github.com/pimoroni/template-python/blob/master/.github/CONTRIBUTING.md)
- [manojmj92/subtitle-downloader](https://github.com/manojmj92/subtitle-downloader)
- [psf/black](https://github.com/psf/black)
- [zavoloklom/material-design-iconic-font](https://github.com/zavoloklom/material-design-iconic-font)
- [rdbende/Sun-Valley-ttk-theme](https://github.com/rdbende/Sun-Valley-ttk-theme)
