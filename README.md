<h1 align="center"><img src="https://raw.githubusercontent.com/vagabondHustler/SubSearch/main/assets/subsearch_v2.png"/></h1>

<div align="center">

![Tests](https://img.shields.io/github/actions/workflow/status/vagabondhustler/subsearch/ci.yml?style=flat-square&labelColor=1e1e2e&label=ci)
![Tags](https://img.shields.io/github/v/tag/vagabondhustler/subsearch?style=flat-square&labelColor=1e1e2e)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/vagabondhustler/subsearch?&style=flat-square&labelColor=1e1e2e)
![License](https://img.shields.io/github/license/vagabondhustler/SUbSearch?&style=flat-square&labelColor=1e1e2e)

![downloads-total)](https://img.shields.io/github/downloads/vagabondhustler/subsearch/total?style=flat-square&label=downloads%40total&labelColor=%231e1e2e)
![downloads-latest)](https://img.shields.io/github/downloads/vagabondhustler/subsearch/latest/total?style=flat-square&label=downloads%40latest&labelColor=%231e1e2e)

</div>

#### Readme Table of Contents

- [About](#about)
- [Preview of GUI](#preview)
- [Install from pypi](#pypi)
- [Clone from github](#clone)
- [Install from MSI Package](#msi)
- [Acknowledgements](#thanks)

#### FAQ Table of Contents

- [GUI Options Explained](https://github.com/vagabondHustler/subsearch/discussions/556)
- [Code Analysis and False Positives](https://github.com/vagabondHustler/subsearch/discussions/557)
- [Supported Languages](https://github.com/vagabondHustler/subsearch/discussions/558)

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

Subsearch is an automated subtitle downloader and extractor with support for many [languages](https://github.com/vagabondHustler/subsearch/discussions/558). It allows users to search and download subtitles for movies and TV shows with a single click from the context menu. The application features a graphical user interface for configuring options, such as selecting which websites to search on, choosing the subtitle language, applying filters for hearing-impaired, among [other options](https://github.com/vagabondHustler/subsearch/discussions/556).

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

## Installation and usage <a name = "getting_started_src"></a>

#### Install from pypi: <a name = "pypi"></a>

Requires Python 3.10+

- Install Subsearch by running `pip install subsearch` in the command prompt.
- Launch the app by running `subsearch` in the command prompt.

#### Clone from github <a name = "clone"></a>

Requires Python *3.10+

- Clone the Subsearch repository by running `git clone https://github.com/vagabondHustler/subsearch.git`.
- Install Subsearch by running `pip install -e .` or *`pip install -e .[build,lint,tests,tools,type]` for optional dependencies.
- Build the executable and MSI installer by running `python -m tools.cx_freeze_build bdist_msi`.

> [!IMPORTANT]  
> ###### If you are using Python 3.12+ and cx_Freeze, please refer to [this issue](https://github.com/marcelotduarte/cx_Freeze/issues/2153).

#### Windows installer <a name = "msi"></a>

Requires windows 10/11, probably works on 8.

- Download the windows installer "Subsearch-x.x.x-win64.msi" from [here](https://github.com/vagabondHustler/subsearch/releases).
- Run the installer.
- If you receive a PUA message, click "More info" → "Run anyway".
- Run Subsearch at least once for all the context menu options to appear

> [!NOTE]  
> ###### Development builds can be located in the [release](https://github.com/vagabondHustler/subsearch/actions/workflows/release.yml) action job, within the generated artifacts.

<details>
<summary>Screenshots of PUA message<a name = "pua"></a></summary>

![prtsc_moreinfo](https://raw.githubusercontent.com/vagabondHustler/SubSearch/main/assets/moreinfo.png)

![prtsc_runanyway](https://raw.githubusercontent.com/vagabondHustler/SubSearch/main/assets/runanyway.png)

---

</details>

More about potentially unwanted applications (PUA) can be found [here](https://support.microsoft.com/en-us/windows/protect-your-pc-from-potentially-unwanted-applications-c7668a25-174e-3b78-0191-faf0607f7a6e) on Microsoft's support page.

## Acknowledgements<a name = "thanks"></a>

I would like to express my gratitude to the following repositories for providing templates, scripts, inspiration, themes, and solutions to similar problems:

- [zavoloklom/material-design-iconic-font](https://github.com/zavoloklom/material-design-iconic-font) // icons
- [rdbende/Sun-Valley-ttk-theme](https://github.com/rdbende/Sun-Valley-ttk-theme) // base theme
- [TransparentLC](https://github.com/TransparentLC) // spritesheet_generator.js
