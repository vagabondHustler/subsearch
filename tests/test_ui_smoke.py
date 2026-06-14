import pytest

from subsearch.runtime.config.defaults import (
    DEFAULT_TOKEN_MULTIPLIERS,
    DEFAULT_TOKEN_WEIGHTS,
)

# Keys written by each card's restore; non-default values used to dirty the store before restoring.
_SUBTITLE_FILTERS_DEFAULTS = {
    "search.hearing_impaired": True,
    "search.non_hearing_impaired": True,
    "search.only_foreign_parts": False,
}

_POST_PROCESSING_DEFAULTS = {
    "post_processing.rename": True,
    "post_processing.move_best": True,
    "post_processing.move_all": False,
}

_PATHS_DEFAULTS = {
    "paths.download_directory": "",
    "paths.extraction_directory": "",
    "paths.video_file_directory": ".",
    "paths.path_resolution": "relative",
    "paths.create_missing_directory": True,
}

_NOTIFICATIONS_DEFAULTS = {
    "notifications.system_tray": True,
    "notifications.summary_notification": False,
}


_APPLICATION_DEFAULTS = {
    "application.show_terminal": False,
    "application.single_instance": True,
}

_NETWORK_DEFAULTS = {
    "network.request_connect_timeout": 4,
    "network.request_read_timeout": 5,
}


def _collect_switch_rows(card):
    from subsearch.ui.widgets.setting_rows import SwitchRow

    return {row.config_key: row for row in card.findChildren(SwitchRow)}


def _collect_slider_rows(card):
    from subsearch.ui.widgets.setting_rows import IntInputRow

    return {row.config_key: row for row in card.findChildren(IntInputRow)}


@pytest.fixture
def settings_window(qtbot):
    from subsearch.ui.application import SettingsWindow

    window = SettingsWindow()
    qtbot.addWidget(window)
    return window


def test_settings_window_builds_every_interface(settings_window, qtbot) -> None:
    stacked = settings_window.stackedWidget
    assert stacked.count() == 8
    for index in range(stacked.count()):
        interface = stacked.widget(index)
        settings_window.switchTo(interface)
        qtbot.waitUntil(lambda current=interface: stacked.currentWidget() is current, timeout=2000)


def test_search_threshold_restore_defaults_resets_all_tuning_values(qtbot) -> None:
    from subsearch.runtime.config import session as config_session
    from subsearch.ui.cards.search_cards import SearchThresholdCard
    from subsearch.ui.state.store import SettingsStore

    store = SettingsStore()
    card = SearchThresholdCard(store)
    qtbot.addWidget(card)
    session = config_session.get_config_session()

    store.write("search.accept_threshold", 50)
    for token_name in DEFAULT_TOKEN_WEIGHTS:
        store.write(f"search.token_weights.{token_name}", 1)
    for token_name in DEFAULT_TOKEN_MULTIPLIERS:
        store.write(f"search.token_multipliers.{token_name}", 0.5)
    assert session.read("search.token_weights.title") == 1
    assert card.slider.value() == 50

    card._restore_defaults()

    assert card.slider.value() == 90
    for token_name, default in DEFAULT_TOKEN_WEIGHTS.items():
        assert session.read(f"search.token_weights.{token_name}") == default
        assert card.tuning_rows[token_name].input.value() == default
    for token_name, default in DEFAULT_TOKEN_MULTIPLIERS.items():
        assert session.read(f"search.token_multipliers.{token_name}") == default
        assert card.tuning_rows[token_name].input.value() == default


def test_file_extensions_card_follows_context_menu_setting_via_store(qtbot) -> None:
    from subsearch.ui.cards.post_processing_cards import FileExtensionsCard
    from subsearch.ui.services.shell_integration import ShellIntegrationService
    from subsearch.ui.state.store import SettingsStore
    from subsearch.ui.state.tasks import TaskRunner

    store = SettingsStore()
    card = FileExtensionsCard(store, ShellIntegrationService(TaskRunner()))
    qtbot.addWidget(card)
    assert all(check_box.isEnabled() for check_box in card.check_boxes.values())

    store.write("shell_integration.context_menu", False)
    assert not any(check_box.isEnabled() for check_box in card.check_boxes.values())

    store.write("shell_integration.context_menu", True)
    assert all(check_box.isEnabled() for check_box in card.check_boxes.values())


def test_subtitle_filters_restore_defaults(qtbot) -> None:
    from subsearch.runtime.config import session as config_session
    from subsearch.ui.cards.search_cards import SubtitleFiltersCard
    from subsearch.ui.state.store import SettingsStore

    store = SettingsStore()
    card = SubtitleFiltersCard(store)
    qtbot.addWidget(card)
    session = config_session.get_config_session()
    switch_rows = _collect_switch_rows(card)

    for key, default in _SUBTITLE_FILTERS_DEFAULTS.items():
        store.write(key, not default)
    for key, default in _SUBTITLE_FILTERS_DEFAULTS.items():
        assert switch_rows[key].switch.isChecked() == (not default)

    card._restore_defaults()

    for key, default in _SUBTITLE_FILTERS_DEFAULTS.items():
        assert session.read(key) == default
        assert switch_rows[key].switch.isChecked() == default


def test_subtitle_handling_restore_defaults(qtbot) -> None:
    from subsearch.runtime.config import session as config_session
    from subsearch.ui.cards.subtitle_handling import SubtitleHandlingCard
    from subsearch.ui.state.store import SettingsStore

    store = SettingsStore()
    card = SubtitleHandlingCard(store)
    qtbot.addWidget(card)
    session = config_session.get_config_session()
    switch_rows = _collect_switch_rows(card)

    store.write("post_processing.rename", False)
    store.write("post_processing.move_best", False)
    assert switch_rows["post_processing.rename"].switch.isChecked() is False
    assert switch_rows["post_processing.move_best"].switch.isChecked() is False

    card._restore_defaults()

    for key, default in _POST_PROCESSING_DEFAULTS.items():
        assert session.read(key) == default
    assert switch_rows["post_processing.rename"].switch.isChecked() is True
    assert switch_rows["post_processing.move_best"].switch.isChecked() is True


def test_paths_restore_defaults(qtbot) -> None:
    from subsearch.runtime.config import session as config_session
    from subsearch.ui.cards.paths import PathsCard
    from subsearch.ui.state.store import SettingsStore

    store = SettingsStore()
    card = PathsCard(store)
    qtbot.addWidget(card)
    session = config_session.get_config_session()

    store.write("paths.video_file_directory", "..\\Subtitles")
    store.write("paths.create_missing_directory", False)

    card._restore_defaults()

    for key, default in _PATHS_DEFAULTS.items():
        assert session.read(key) == default


def test_shell_integration_restore_re_enables_context_menu_icon(qtbot) -> None:
    from subsearch.ui.cards.post_processing_cards import ShellIntegrationCard
    from subsearch.ui.services.shell_integration import ShellIntegrationService
    from subsearch.ui.state.store import SettingsStore
    from subsearch.ui.state.tasks import TaskRunner

    store = SettingsStore()
    card = ShellIntegrationCard(store, ShellIntegrationService(TaskRunner()))
    qtbot.addWidget(card)

    # Disabling context_menu disables the icon row.
    store.write("shell_integration.context_menu", False)
    assert not card.context_menu_icon.switch.isEnabled()

    card._restore_defaults()

    # Default has context_menu=True, so the icon row must be re-enabled after restore.
    assert card.context_menu_icon.switch.isEnabled()


def test_notifications_restore_defaults(qtbot) -> None:
    from subsearch.runtime.config import session as config_session
    from subsearch.ui.cards.system_cards import NotificationsCard
    from subsearch.ui.state.store import SettingsStore

    store = SettingsStore()
    card = NotificationsCard(store)
    qtbot.addWidget(card)
    session = config_session.get_config_session()
    switch_rows = _collect_switch_rows(card)

    store.write("notifications.system_tray", False)
    store.write("notifications.summary_notification", True)
    assert switch_rows["notifications.system_tray"].switch.isChecked() is False
    assert switch_rows["notifications.summary_notification"].switch.isChecked() is True

    card._restore_defaults()

    for key, default in _NOTIFICATIONS_DEFAULTS.items():
        assert session.read(key) == default
        assert switch_rows[key].switch.isChecked() == default


def test_search_mode_restore_defaults(qtbot) -> None:
    from subsearch.runtime.config import session as config_session
    from subsearch.ui.cards.search_cards import SearchModeCard
    from subsearch.ui.state.store import SettingsStore
    from subsearch.ui.widgets.setting_rows import FuzzySelectRow

    store = SettingsStore()
    card = SearchModeCard(store)
    qtbot.addWidget(card)
    session = config_session.get_config_session()
    combo_rows = {row.config_key: row for row in card.findChildren(FuzzySelectRow)}

    store.write("download_manager.search_mode", "manual")
    assert combo_rows["download_manager.search_mode"].combo_box.currentText() == "Manual"

    card._restore_defaults()

    assert session.read("download_manager.search_mode") == "hybrid"


def test_subtitle_handling_greys_out_automatic_rows_when_manually_handle_enabled(qtbot) -> None:
    from subsearch.ui.cards.subtitle_handling import SubtitleHandlingCard
    from subsearch.ui.state.store import SettingsStore

    store = SettingsStore()
    card = SubtitleHandlingCard(store)
    qtbot.addWidget(card)

    assert card._automatic_handling.isEnabled()

    store.write("download_manager.manually_handle_post_processing", True)
    assert not card._automatic_handling.isEnabled()
    # The card itself stays usable.
    assert card.isEnabled()

    store.write("download_manager.manually_handle_post_processing", False)
    assert card._automatic_handling.isEnabled()


def test_application_restore_defaults(qtbot) -> None:
    from subsearch.runtime.config import session as config_session
    from subsearch.ui.cards.system_cards import ApplicationCard
    from subsearch.ui.services.shell_integration import ShellIntegrationService
    from subsearch.ui.state.store import SettingsStore
    from subsearch.ui.state.tasks import TaskRunner

    store = SettingsStore()
    card = ApplicationCard(store, ShellIntegrationService(TaskRunner()))
    qtbot.addWidget(card)
    session = config_session.get_config_session()
    switch_rows = _collect_switch_rows(card)

    store.write("application.show_terminal", True)
    store.write("application.single_instance", False)
    assert switch_rows["application.show_terminal"].switch.isChecked() is True
    assert switch_rows["application.single_instance"].switch.isChecked() is False

    card._restore_defaults()

    for key, default in _APPLICATION_DEFAULTS.items():
        assert session.read(key) == default
        assert switch_rows[key].switch.isChecked() == default


def test_network_restore_defaults(qtbot) -> None:
    from subsearch.runtime.config import session as config_session
    from subsearch.ui.cards.system_cards import NetworkCard
    from subsearch.ui.state.store import SettingsStore

    store = SettingsStore()
    card = NetworkCard(store)
    qtbot.addWidget(card)
    session = config_session.get_config_session()
    slider_rows = _collect_slider_rows(card)

    store.write("network.request_connect_timeout", 10)
    store.write("network.request_read_timeout", 10)
    assert slider_rows["network.request_connect_timeout"].input.value() == 10
    assert slider_rows["network.request_read_timeout"].input.value() == 10

    card._restore_defaults()

    for key, default in _NETWORK_DEFAULTS.items():
        assert session.read(key) == default
        assert slider_rows[key].input.value() == default


def test_slider_edit_enter_commits_and_clamps(qtbot) -> None:
    from subsearch.ui.widgets.slider import SliderWithValueLabel

    slider = SliderWithValueLabel(suffix="%")
    qtbot.addWidget(slider)
    slider.setRange(0, 100)
    slider.set_value_silent(40)
    assert slider._edit.text() == "40 %"

    slider._edit.setText("150")
    slider.commit_edit()

    assert slider.value() == 100
    assert slider._edit.text() == "100 %"


def test_int_input_row_writes_committed_value_to_store(qtbot) -> None:
    from subsearch.ui.state.store import SettingsStore
    from subsearch.ui.widgets.setting_rows import IntInputRow

    store = SettingsStore()
    row = IntInputRow("search.downloads_per_provider", store, 1, 99)
    qtbot.addWidget(row)

    row.input.setText("250")
    row.input._commit()

    assert row.input.value() == 99
    assert store.read("search.downloads_per_provider") == 99


def test_extraction_directory_accepts_empty_and_rejects_invalid_path(qtbot) -> None:
    from subsearch.ui.state.store import SettingsStore
    from subsearch.ui.widgets.setting_rows import DirectoryPathRow

    store = SettingsStore()
    row = DirectoryPathRow("paths.extraction_directory", store, allow_empty=True)
    qtbot.addWidget(row)

    row.path_edit.setText("")
    assert row.is_valid()
    row.save_if_valid()
    assert store.read("paths.extraction_directory") == ""

    row.path_edit.setText("::not a path::")
    assert not row.is_valid()
    assert row.path_edit.property("error") is True
    row.save_if_valid()
    assert store.read("paths.extraction_directory") == ""
