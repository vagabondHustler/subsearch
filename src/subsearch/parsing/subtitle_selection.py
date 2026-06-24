from pathlib import Path

from subsearch.io import file_system
from subsearch.parsing import release_parser
from subsearch.runtime.config import session as config_session
from subsearch.runtime.config.defaults import ConfigKey


def find_best_subtitle_match(release_name: str, subs_dir: Path) -> Path:
    config = config_session.get_config_session()
    return release_parser.rank_best_subtitle(
        file_system.subtitle_files_in(subs_dir),
        release_name,
        config.read(ConfigKey.SEARCH_TOKEN_WEIGHTS),
        config.read(ConfigKey.SEARCH_TOKEN_MULTIPLIERS),
        config.read(ConfigKey.SEARCH_ACCEPT_THRESHOLD),
    )


def autoload_rename(release_name: str, subs_dir: Path) -> Path:
    matched_file = find_best_subtitle_match(release_name, subs_dir)
    return file_system.rename_subtitle_to_release(matched_file, release_name, matched_file.suffix)
