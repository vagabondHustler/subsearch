from types import SimpleNamespace

import pytest

from subsearch.parsing import imdb_lookup


@pytest.fixture(autouse=True)
def _load_imdbinfo() -> None:
    imdb_lookup._load_imdbinfo()


def _fake_search_result(titles: list[SimpleNamespace]) -> SimpleNamespace:
    return SimpleNamespace(titles=titles)


def _fake_title(title: str, year: int | None, kind: str, imdb_id: str) -> SimpleNamespace:
    return SimpleNamespace(title=title, year=year, kind=kind, imdbId=imdb_id)


def test_find_title_suggestions_returns_movies_and_series(monkeypatch) -> None:
    titles = [
        _fake_title("The Terminator", 1984, "movie", "tt0088247"),
        _fake_title("Terminator 2: Judgment Day", 1991, "movie", "tt0103064"),
        _fake_title("Terminator: The Sarah Connor Chronicles", 2008, "tvSeries", "tt0851851"),
        _fake_title("Terminator Soundtrack", 1984, "music", "tt9999999"),
    ]
    monkeypatch.setattr(imdb_lookup.imdbinfo, "search_title", lambda term: _fake_search_result(titles))

    suggestions = imdb_lookup.find_title_suggestions("the terminator")

    assert [suggestion.imdb_id for suggestion in suggestions] == ["tt0088247", "tt0103064", "tt0851851"]
    assert suggestions[0].search_term() == "The Terminator (1984)"
    assert suggestions[2].tvseries is True
    assert suggestions[2].search_term() == "Terminator: The Sarah Connor Chronicles"


def test_find_title_suggestions_respects_limit(monkeypatch) -> None:
    titles = [_fake_title(f"Movie {index}", 2000 + index, "movie", f"tt{index}") for index in range(10)]
    monkeypatch.setattr(imdb_lookup.imdbinfo, "search_title", lambda term: _fake_search_result(titles))

    assert len(imdb_lookup.find_title_suggestions("movie")) == imdb_lookup.SUGGESTION_LIMIT


def test_find_title_suggestions_empty_on_lookup_error(monkeypatch) -> None:
    def raise_error(term: str) -> None:
        raise imdb_lookup.ImdbinfoError("boom")

    monkeypatch.setattr(imdb_lookup.imdbinfo, "search_title", raise_error)

    assert imdb_lookup.find_title_suggestions("the terminator") == []


def test_suggestion_display_text() -> None:
    movie = imdb_lookup.TitleSuggestion("The Terminator", 1984, False, "tt0088247")
    series = imdb_lookup.TitleSuggestion("Breaking Bad", 2008, True, "tt0903747")

    assert movie.display_text() == "The Terminator (1984)"
    assert series.display_text() == "Breaking Bad (2008)  ·  TV series"
