from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class SearchSubject:
    file_exists: bool
    search_term: str
    file_hash: str
    file_extension: str
    file_path: Path | None

    def copy_from(self, other: "SearchSubject") -> None:
        for field_name in self.__slots__:
            setattr(self, field_name, getattr(other, field_name))


@dataclass(slots=True)
class Workspace:
    file_directory: Path
    extraction_directory: Path
    download_directory: Path

    def copy_from(self, other: "Workspace") -> None:
        for field_name in self.__slots__:
            setattr(self, field_name, getattr(other, field_name))


@dataclass(slots=True)
class ReleaseInfo:
    title: str
    year: int
    season: str
    season_ordinal: str
    episode: str
    episode_ordinal: str
    tvseries: bool
    release: str
    group: str
    imdb_id: str
