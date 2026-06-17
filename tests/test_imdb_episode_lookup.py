from dataclasses import dataclass

from imdbinfo.exceptions import ImdbinfoError

from subsearch.parsing import imdb_lookup
from subsearch.parsing.imdb_lookup import (
    find_episode_suggestions,
    find_season_suggestions,
)


@dataclass
class _FakeEpisode:
    season: int
    episode: int
    title: str


@dataclass
class _FakeSeasonEpisodes:
    total_series_seasons: int
    episodes: list[_FakeEpisode]


def test_find_season_suggestions_lists_every_season(monkeypatch) -> None:
    monkeypatch.setattr(
        imdb_lookup.imdbinfo,
        "get_episodes",
        lambda imdb_id, season=1: _FakeSeasonEpisodes(total_series_seasons=3, episodes=[]),
    )
    suggestions = find_season_suggestions("tt0903747")
    assert [suggestion.number for suggestion in suggestions] == [1, 2, 3]


def test_find_episode_suggestions_carries_season_and_title(monkeypatch) -> None:
    episodes = [
        _FakeEpisode(season=2, episode=1, title="Seven Thirty-Seven"),
        _FakeEpisode(season=2, episode=2, title=""),
    ]
    monkeypatch.setattr(
        imdb_lookup.imdbinfo,
        "get_episodes",
        lambda imdb_id, season=1: _FakeSeasonEpisodes(total_series_seasons=5, episodes=episodes),
    )
    suggestions = find_episode_suggestions("tt0903747", season=2)
    assert [(suggestion.season, suggestion.number) for suggestion in suggestions] == [(2, 1), (2, 2)]
    assert suggestions[0].display_text() == "Episode 1  ·  Seven Thirty-Seven"
    assert suggestions[1].display_text() == "Episode 2"


def test_find_season_suggestions_returns_empty_on_lookup_error(monkeypatch) -> None:
    def _raise(imdb_id, season=1):
        raise ImdbinfoError("offline")

    monkeypatch.setattr(imdb_lookup.imdbinfo, "get_episodes", _raise)
    assert find_season_suggestions("tt0903747") == []
    assert find_episode_suggestions("tt0903747", season=1) == []
