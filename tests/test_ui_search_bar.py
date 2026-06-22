import warnings

from subsearch.ui.widgets.suggestion_popup import NumberSuggestionPopup


def build_search_bar(qtbot):
    from subsearch.ui.cards.subtitle_workspace.search_bar import SubtitleSearchBar
    from subsearch.ui.services.video_file import VideoFileService
    from subsearch.ui.state.store import SettingsStore

    search_bar = SubtitleSearchBar(SettingsStore(), VideoFileService())
    qtbot.addWidget(search_bar)
    return search_bar


def test_reconnect_number_chosen_first_call_emits_no_disconnect_warning(qtbot) -> None:
    search_bar = build_search_bar(qtbot)
    popup = NumberSuggestionPopup(search_bar)
    qtbot.addWidget(popup)

    with warnings.catch_warnings():
        warnings.simplefilter("error", RuntimeWarning)
        # First reconnect has nothing connected; it must not try to disconnect an
        # empty signal (which makes PySide raise a "Failed to disconnect" warning).
        search_bar._reconnect_number_chosen(popup, search_bar._on_season_chosen)


def test_reconnect_number_chosen_swaps_slot_so_only_latest_fires(qtbot) -> None:
    search_bar = build_search_bar(qtbot)
    popup = NumberSuggestionPopup(search_bar)
    qtbot.addWidget(popup)

    season_calls: list[int] = []
    episode_calls: list[int] = []
    search_bar._reconnect_number_chosen(popup, season_calls.append)
    search_bar._reconnect_number_chosen(popup, episode_calls.append)

    popup.number_chosen.emit(7)

    assert season_calls == []
    assert episode_calls == [7]
