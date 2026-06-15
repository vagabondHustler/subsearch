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

Subsearch is a Windows subtitle downloader that integrates with the right-click context menu. Select a media file, click **Search subtitles**, and matching subtitles are downloaded and extracted automatically.

#### Features

- Right-click any media file to trigger a search
- 70+ languages supported
- Filters: hearing-impaired, non-HI, foreign parts only
- Configurable via a GUI 
- Available as an MSI installer, PyPI package, or source

Links: [Supported languages](https://github.com/vagabondHustler/subsearch/discussions/558) · [Contributing](https://github.com/vagabondHustler/SubSearch/blob/main/.github/CONTRIBUTING.md) · [Security](https://github.com/vagabondHustler/SubSearch/blob/main/.github/SECURITY.md)

---

## Preview

<div align="center">

![example](https://raw.githubusercontent.com/vagabondHustler/SubSearch/main/assets/example.gif)

![ui](https://github.com/vagabondHustler/subsearch/blob/main/assets/ui_full.png?raw=true)

</div>

---

## Installation

#### Windows installer (recommended)

Requires Windows 10/11.

1. Download the installer from the [releases page](https://github.com/vagabondHustler/subsearch/releases).
2. Run the installer. If a SmartScreen / PUA warning appears, click **More info → Run anyway** ([why?](https://support.microsoft.com/en-us/windows/protect-your-pc-from-potentially-unwanted-applications-c7668a25-174e-3b78-0191-faf0607f7a6e))
3. Launch Subsearch once to register the context menu entries.

<details>
<summary>PUA warning screenshots</summary>

![moreinfo](https://raw.githubusercontent.com/vagabondHustler/SubSearch/main/assets/moreinfo.png)
![runanyway](https://raw.githubusercontent.com/vagabondHustler/SubSearch/main/assets/runanyway.png)

</details>

Development builds are available as artifacts in the [release action](https://github.com/vagabondHustler/subsearch/actions/workflows/release.yml).

#### PyPI

```
pip install subsearch
subsearch
```

#### Source

```
git clone https://github.com/vagabondHustler/subsearch.git
pip install -e .
```

Use `pip install -e .[build,lint,tests,tools,type]` to include optional dev dependencies. Run `python -m tools.cx_freeze_build bdist_msi` to build the MSI.

## License

Subsearch is licensed under the GNU General Public License v3.0 (or later); see `LICENSE` for the full text.

The distributed application bundles third-party components listed in `THIRD-PARTY-LICENSES.md`. Notably PySide6 (Qt for Python) under LGPL v3 and PySide6-Fluent-Widgets under GPL v3, the latter is why Subsearch as a whole is distributed under GPL v3.
