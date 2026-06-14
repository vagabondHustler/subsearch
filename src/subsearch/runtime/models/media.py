from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class VideoFile:
    file_exists: bool
    filename: str
    file_hash: str
    file_extension: str
    file_path: Path
    file_directory: Path
    extraction_directory: Path
    download_directory: Path

    def copy_from(self, other: "VideoFile") -> None:
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
