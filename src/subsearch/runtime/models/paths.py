from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class AppPaths:
    home: Path
    data: Path
    ui_assets: Path
    providers: Path
    io: Path
    parsing: Path
    tmp_dir: Path
    appdata_subsearch: Path


@dataclass(slots=True)
class FilePaths:
    log: Path
    crash: Path
    config: Path
    subtitle_languages: Path


@dataclass(slots=True)
class ProviderUrls:
    opensubtitles: list[str]
    opensubtitles_hash: list[str]
    yifysubtitles: list[str]
    subsource: list[str]
    tvsubtitles: list[str]


@dataclass(slots=True, frozen=True)
class WindowsRegistryPaths:
    classes: str
    asterisk: str
    shell: str
    subsearch: str
    subsearch_command: str
    long_paths: str
