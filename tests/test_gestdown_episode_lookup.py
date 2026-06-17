from subsearch.parsing.gestdown_lookup import GestdownLookup


class _FakeResponse:
    def __init__(self, status_code: int, payload: dict) -> None:
        self.status_code = status_code
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class _FakeSession:
    def __init__(self, responses: dict[str, _FakeResponse]) -> None:
        self._responses = responses
        self.requested_urls: list[str] = []

    def get(self, url: str) -> _FakeResponse:
        self.requested_urls.append(url)
        for fragment, response in self._responses.items():
            if fragment in url:
                return response
        return _FakeResponse(404, {})


_SEARCH_PAYLOAD = {
    "shows": [
        {"id": "show-uuid", "name": "Breaking Bad", "nbSeasons": 5, "seasons": [1, 2, 3, 4, 5]},
        {"id": "minisodes-uuid", "name": "Breaking Bad Minisodes", "nbSeasons": 1, "seasons": [1]},
    ]
}


def _lookup_with(responses: dict[str, _FakeResponse]) -> tuple[GestdownLookup, _FakeSession]:
    lookup = GestdownLookup()
    session = _FakeSession(responses)
    lookup.session = session
    return lookup, session


def test_find_season_suggestions_uses_show_seasons() -> None:
    lookup, _ = _lookup_with({"shows/search": _FakeResponse(200, _SEARCH_PAYLOAD)})
    suggestions = lookup.find_season_suggestions("Breaking Bad")
    assert [suggestion.number for suggestion in suggestions] == [1, 2, 3, 4, 5]


def test_find_season_suggestions_prefers_exact_name_match() -> None:
    lookup, _ = _lookup_with({"shows/search": _FakeResponse(200, _SEARCH_PAYLOAD)})
    suggestions = lookup.find_season_suggestions("Breaking Bad")
    assert len(suggestions) == 5


def test_find_episode_suggestions_carries_season_and_title() -> None:
    episodes_payload = {
        "episodes": [
            {"season": 4, "number": 1, "title": "Box Cutter"},
            {"season": 4, "number": 2, "title": None},
            {"season": 4, "number": 0, "title": "Sneak Peek"},
        ]
    }
    lookup, session = _lookup_with(
        {
            "shows/search": _FakeResponse(200, _SEARCH_PAYLOAD),
            "shows/show-uuid": _FakeResponse(200, episodes_payload),
        }
    )
    suggestions = lookup.find_episode_suggestions("Breaking Bad", season=4, language_name="English")
    assert [(suggestion.season, suggestion.number) for suggestion in suggestions] == [(4, 1), (4, 2)]
    assert suggestions[0].display_text() == "Episode 1  ·  Box Cutter"
    assert any("show-uuid/4/English" in url for url in session.requested_urls)


def test_find_season_suggestions_empty_when_show_not_found() -> None:
    lookup, _ = _lookup_with({"shows/search": _FakeResponse(404, {})})
    assert lookup.find_season_suggestions("Nonexistent Show") == []


def test_find_episode_suggestions_empty_when_season_unavailable() -> None:
    lookup, _ = _lookup_with(
        {
            "shows/search": _FakeResponse(200, _SEARCH_PAYLOAD),
            "shows/show-uuid": _FakeResponse(404, {}),
        }
    )
    assert lookup.find_episode_suggestions("Breaking Bad", season=9, language_name="English") == []
