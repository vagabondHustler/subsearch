from pathlib import Path
from typing import Callable

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from subsearch.parsing.imdb_lookup import (
    EpisodeSuggestion,
    SeasonSuggestion,
    TitleSuggestion,
)
from subsearch.parsing.release_parser import get_release_info
from subsearch.runtime.config import SEARCH_SUBJECT
from subsearch.runtime.config.defaults import ConfigKey
from subsearch.runtime.logging.events import LogEvent
from subsearch.runtime.logging.logger import log
from subsearch.ui.cards.subtitle_workspace._constants import SEARCH_BAR_WIDTH_FRACTION
from subsearch.ui.services.season_episode_suggestions import (
    SeasonEpisodeSuggestionService,
)
from subsearch.ui.services.title_suggestions import TitleSuggestionService
from subsearch.ui.services.video_file import VideoFileService
from subsearch.ui.state.store import SettingsStore
from subsearch.ui.theme.separators import SEPARATOR_INSET
from subsearch.ui.widgets.search_line_edit import SearchLineEdit
from subsearch.ui.widgets.suggestion_popup import (
    NumberSuggestionPopup,
    TitleSuggestionPopup,
)


class SubtitleSearchBar(QWidget):
    research_requested = Signal(str, object)

    def __init__(
        self,
        store: SettingsStore,
        video_file_service: VideoFileService,
        title_suggestion_service: TitleSuggestionService | None = None,
        season_episode_suggestion_service: SeasonEpisodeSuggestionService | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.store = store
        self._video_file_service = video_file_service
        self._title_suggestion_service = title_suggestion_service
        self._season_episode_suggestion_service = season_episode_suggestion_service
        self._awaiting_suggestions = False
        self._term_without_suggestions = ""
        self._committed_filename = SEARCH_SUBJECT.name if SEARCH_SUBJECT.file_exists else ""
        self._pending_series: TitleSuggestion | None = None
        self._pending_season = 0
        self._number_chosen_slot: Callable[..., None] | None = None
        if title_suggestion_service is not None:
            title_suggestion_service.suggestions_ready.connect(self._on_suggestions_ready)
            title_suggestion_service.lookup_failed.connect(self._on_suggestion_lookup_failed)
        if season_episode_suggestion_service is not None:
            season_episode_suggestion_service.seasons_ready.connect(self._on_seasons_ready)
            season_episode_suggestion_service.episodes_ready.connect(self._on_episodes_ready)
            season_episode_suggestion_service.lookup_failed.connect(self._on_season_episode_lookup_failed)

        self._build_video_file_section()
        store.subscribe(ConfigKey.SEARCH_PROVIDERS, self._on_providers_changed)
        self._on_providers_changed(store.read(ConfigKey.SEARCH_PROVIDERS))

    def _on_providers_changed(self, providers: dict) -> None:
        all_disabled = not any(providers.values())
        self._filename_edit.set_button_enabled(not all_disabled)
        if all_disabled:
            self._filename_edit.set_button_tooltip("Enable at least one subtitle provider to search")
        else:
            self._filename_edit.set_button_tooltip("Search for subtitles")

    def _build_video_file_section(self) -> None:
        section_layout = QVBoxLayout(self)
        section_layout.setContentsMargins(0, 0, 0, 0)

        self._filename_edit = SearchLineEdit("Search for subtitles", parent=self)
        self._filename_edit.setText(
            SEARCH_SUBJECT.search_term + SEARCH_SUBJECT.file_extension if SEARCH_SUBJECT.file_exists else ""
        )
        self._filename_edit.editingFinished.connect(self._on_filename_edited)
        self._filename_edit.returnPressed.connect(self._on_search_clicked)
        self._filename_edit.button_clicked.connect(self._on_search_clicked)

        file_row = QHBoxLayout()
        file_row.setContentsMargins(SEPARATOR_INSET, 0, SEPARATOR_INSET, 10)
        file_row.setSpacing(0)
        side_stretch = round((1 - SEARCH_BAR_WIDTH_FRACTION) * 100 / 2)
        file_row.addStretch(side_stretch)
        file_row.addWidget(self._filename_edit, stretch=round(SEARCH_BAR_WIDTH_FRACTION * 100))
        file_row.addStretch(side_stretch)
        section_layout.addLayout(file_row)

    def _on_search_clicked(self) -> None:
        if self._awaiting_suggestions:
            return
        # Tool buttons do not take focus on click, so editingFinished never fires
        # for a typed search term; commit the field before starting the search.
        self._on_filename_edited()
        typed_term = self._filename_edit.text().strip()
        suggestion_service = self._title_suggestion_service
        if suggestion_service is not None and self._needs_title_suggestions(typed_term):
            self._awaiting_suggestions = True
            self.start_spinner()
            suggestion_service.request(typed_term)
            return
        self.research_requested.emit("", None)

    def start_spinner(self) -> None:
        self._filename_edit.start_spinner()

    def stop_spinner(self) -> None:
        self._filename_edit.stop_spinner()

    def _needs_title_suggestions(self, typed_term: str) -> bool:
        if not typed_term:
            return False
        if typed_term == self._term_without_suggestions:
            return False
        release_info = get_release_info(typed_term)
        return release_info.year == 0 and not release_info.tvseries

    def _on_suggestions_ready(self, typed_term: str, suggestions: list[TitleSuggestion]) -> None:
        if not self._awaiting_suggestions:
            return
        self._awaiting_suggestions = False
        if not suggestions:
            # No popup; the spinner keeps running straight into the search.
            self._search_as_typed(typed_term)
            return
        self.stop_spinner()
        self._suggestion_popup().show_suggestions(suggestions)

    def _on_suggestion_lookup_failed(self, _message: str) -> None:
        if not self._awaiting_suggestions:
            return
        self._awaiting_suggestions = False
        self._search_as_typed(self._filename_edit.text().strip())

    def _suggestion_popup(self) -> TitleSuggestionPopup:
        popup = getattr(self, "_title_suggestion_popup", None)
        if popup is None:
            popup = TitleSuggestionPopup(self._filename_edit)
            popup.suggestion_accepted.connect(self._on_suggestion_accepted)
            popup.dismissed.connect(self._on_suggestions_dismissed)
            self._title_suggestion_popup = popup
        return popup

    def _on_suggestion_accepted(self, suggestion: TitleSuggestion) -> None:
        if suggestion.tvseries and self._season_episode_suggestion_service is not None:
            self._pending_series = suggestion
            self.start_spinner()
            self._season_episode_suggestion_service.request_seasons(suggestion.title, suggestion.imdb_id)
            return
        self._commit_term_and_search(suggestion.search_term(), suggestion.imdb_id, suggestion.tvseries)

    def _on_seasons_ready(self, seasons: list[SeasonSuggestion]) -> None:
        if self._pending_series is None:
            return
        self.stop_spinner()
        numbers = [season.number for season in seasons]
        labels = [season.display_text() for season in seasons]
        popup = self._number_popup()
        self._reconnect_number_chosen(popup, self._on_season_chosen)
        popup.show_numbers(numbers, labels)

    def _on_season_chosen(self, season: int) -> None:
        if self._pending_series is None or self._season_episode_suggestion_service is None:
            return
        self._pending_season = season
        self.start_spinner()
        self._season_episode_suggestion_service.request_episodes(
            self._pending_series.title, self._pending_series.imdb_id, season, self._selected_language_name()
        )

    def _on_episodes_ready(self, season: int, episodes: list[EpisodeSuggestion]) -> None:
        if self._pending_series is None or season != self._pending_season:
            return
        self.stop_spinner()
        numbers = [episode.number for episode in episodes]
        labels = [episode.display_text() for episode in episodes]
        popup = self._number_popup()
        self._reconnect_number_chosen(popup, self._on_episode_chosen)
        popup.show_numbers(numbers, labels)

    def _on_episode_chosen(self, episode: int) -> None:
        if self._pending_series is None:
            return
        series = self._pending_series
        log.event(
            LogEvent.SEARCH_SEASON_EPISODE_CHOSEN,
            level="debug",
            title=series.title,
            season=self._pending_season,
            episode=episode,
        )
        term = f"{series.title} S{self._pending_season:02d}E{episode:02d}"
        self._reset_pending_series()
        self._commit_term_and_search(term, series.imdb_id, True)

    def _on_season_episode_lookup_failed(self, _message: str) -> None:
        if self._pending_series is None:
            return
        # IMDb is unreachable: fall back to a series-level search the user can refine.
        series = self._pending_series
        self._reset_pending_series()
        self._commit_term_and_search(series.search_term(), series.imdb_id, True)

    def _selected_language_name(self) -> str:
        selected = self.store.read(ConfigKey.LANGUAGE_SELECTED)
        return str(self.store.language_data()[selected]["name"])

    def _reset_pending_series(self) -> None:
        self._pending_series = None
        self._pending_season = 0

    def _reconnect_number_chosen(self, popup: NumberSuggestionPopup, slot: Callable[..., None]) -> None:
        # The popup is reused across the season then episode step. Drop the prior
        # step's slot first, otherwise choosing the episode also fires the season
        # handler and clobbers _pending_season with the episode number. Only
        # disconnect a slot we actually connected; disconnecting an empty signal
        # makes PySide emit a "Failed to disconnect (None)" RuntimeWarning.
        if self._number_chosen_slot is not None:
            popup.number_chosen.disconnect(self._number_chosen_slot)
        popup.number_chosen.connect(slot)
        self._number_chosen_slot = slot

    def _number_popup(self) -> NumberSuggestionPopup:
        popup = getattr(self, "_season_episode_popup", None)
        if popup is None:
            popup = NumberSuggestionPopup(self._filename_edit)
            popup.dismissed.connect(self._on_season_episode_dismissed)
            self._season_episode_popup = popup
        return popup

    def _on_season_episode_dismissed(self) -> None:
        if self._pending_series is None:
            return
        series = self._pending_series
        self._reset_pending_series()
        self._commit_term_and_search(series.search_term(), series.imdb_id, True)

    def _commit_term_and_search(self, term: str, imdb_id: str, tvseries: bool) -> None:
        self._filename_edit.setText(term)
        self._term_without_suggestions = term
        self._on_filename_edited()
        self.research_requested.emit(imdb_id, tvseries)

    def _on_suggestions_dismissed(self) -> None:
        self._search_as_typed(self._filename_edit.text().strip())

    def _search_as_typed(self, typed_term: str) -> None:
        self._term_without_suggestions = typed_term
        self._on_filename_edited()
        self.research_requested.emit("", None)

    def _on_filename_edited(self) -> None:
        filename = self._filename_edit.text().strip()
        if not filename or filename == self._committed_filename:
            return
        self._committed_filename = filename
        self._video_file_service.rename_active_video(filename)

    def select_dropped_video(self, file_path: Path) -> None:
        self._filename_edit.setText(file_path.name)
        self._term_without_suggestions = file_path.name
        self._committed_filename = file_path.name
        self._video_file_service.select_video(file_path)
