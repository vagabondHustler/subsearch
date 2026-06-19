<h1 align="center"><img src="https://raw.githubusercontent.com/vagabondHustler/SubSearch/main/assets/subsearch_v2.png"/></h1>

<div align="center">

![ci](https://img.shields.io/github/actions/workflow/status/vagabondhustler/subsearch/ci.yml?style=flat-square&labelColor=1e1e2e&label=ci)
![commit](https://img.shields.io/github/last-commit/vagabondhustler/subsearch?style=flat-square&labelColor=1e1e2e&label=commit%20activity)
![python](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2FvagabondHustler%2Fsubsearch%2Fmain%2Fpyproject.toml&style=flat-square&labelColor=1e1e2e)
![release](https://img.shields.io/github/v/tag/vagabondhustler/subsearch?style=flat-square&labelColor=1e1e2e&label=latest%20release)
![downloads](https://img.shields.io/github/downloads/vagabondhustler/subsearch/total?style=flat-square&labelColor=%231e1e2e&label=downloads)
![license](https://img.shields.io/github/license/vagabondhustler/subsearch?style=flat-square&labelColor=1e1e2e)

</div>

---

Subsearch is a Windows subtitle downloader with File Explorer integration, a PySide6 desktop UI, and a Subtitle
Workspace for searching, reviewing, downloading, and post-processing subtitles.

Use it as a quiet right-click workflow, a fully manual download manager, or a mix of both. Subsearch tries to download
the best match automatically and opens the workspace only when you need to choose one yourself.

#### Highlights

- Right-click video files in File Explorer, drag files into the app, or search by title from the workspace
- Manual, hybrid, and automatic search modes
- Providers: OpenSubtitles, YIFY Subtitles, Subsource, TVsubtitles, and Gestdown
- 115 subtitle languages, with provider compatibility handled for each language
- Movie and TV matching with IMDb title suggestions and season and episode selection
- Adjustable filename scoring for title, source, release group, year, season/episode, and edition mismatches
- Filters for hearing-impaired, non-HI, and foreign-parts-only subtitles
- Post-processing to extract, rename, and move the best subtitle or every downloaded subtitle
- Configurable download, extraction, and destination paths, including relative paths next to the video
- Windows notifications, system tray support, single-instance mode, update checks, crash logs, and provider diagnostics
- Available as a Windows MSI installer, a PyPI package, or a source install

<div align="center">

#### [False positives](https://github.com/vagabondHustler/subsearch/discussions/557) · [Contributing](https://github.com/vagabondHustler/SubSearch/blob/main/.github/CONTRIBUTING.md) · [Security](https://github.com/vagabondHustler/SubSearch/blob/main/.github/SECURITY.md)

</div>
---

## Preview

<div align="center">

![example](https://raw.githubusercontent.com/vagabondHustler/SubSearch/main/assets/example.gif)

![ui](https://github.com/vagabondHustler/subsearch/blob/main/assets/ui_full.png?raw=true)

</div>

---

## Installation

#### Windows installer

Requires Windows 10 or 11. It may also work on Windows 8.

1. Download the installer from the [releases page](https://github.com/vagabondHustler/subsearch/releases).
2. Run the installer. If a SmartScreen or PUA warning appears, select **More info**, then **Run anyway**. ([More information](https://support.microsoft.com/en-us/windows/protect-your-pc-from-potentially-unwanted-applications-c7668a25-174e-3b78-0191-faf0607f7a6e))
3. Launch Subsearch once to register its File Explorer context-menu entries.

<details>
<summary>PUA warning screenshots</summary>

![moreinfo](https://raw.githubusercontent.com/vagabondHustler/SubSearch/main/assets/moreinfo.png)
![runanyway](https://raw.githubusercontent.com/vagabondHustler/SubSearch/main/assets/runanyway.png)

</details>

#### Install from PyPI

```
pip install subsearch
subsearch
```

#### Clone from GitHub

```
git clone https://github.com/vagabondHustler/subsearch.git
cd subsearch
pip install -e .
```

To install the optional development dependencies, run:

```
pip install -e .[build,lint,tests,tools,type]
```

Build the MSI with cx_Freeze:

```
python .github/workflows/scripts/jobs.py make_msi
```

## License

- Subsearch is licensed under the GNU General Public License v3.0 or later. See `LICENSE` for the full text.
- Third-party notices are listed in `THIRD-PARTY-LICENSES.md`.
