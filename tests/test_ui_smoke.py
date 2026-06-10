import pytest

from subsearch.runtime.config.static_values import (
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
    "post_processing.target_path": ".",
    "post_processing.path_resolution": "relative",
    "post_processing.create_missing_folder": True,
}

_NOTIFICATIONS_DEFAULTS = {
    "notifications.system_tray": True,
    "notifications.summary_notification": False,
}

_DOWNLOAD_MANAGER_DEFAULTS = {
    "download.automatic": True,
    "download.always_open_manager": False,
    "download.open_manager_on_no_matches": True,
}

_APPLICATION_DEFAULTS = {
    "application.show_terminal": False,
    "application.single_instance": True,
}

_NETWORK_DEFAULTS = {
    "network.api_call_limit": 4,
    "network.request_connect_timeout": 4,
    "network.request_read_timeout": 5,
}


@pytest.fixture
def settings_window(qtbot):
    from subsearch.ui.application import SettingsWindow

    window = SettingsWindow()
    qtbot.addWidget(window)
    return window


def test_settings_window_builds_every_interface(settings_window, qtbot) -> None:
    stacked = settings_window.stackedWidget
    assert stacked.count() == 6
    for index in range(stacked.count()):
        interface = stacked.widget(index)
        settings_window.switchTo(interface)
        qtbot.waitUntil(lambda current=interface: stacked.currentWidget() is current, timeout=2000)


def test_search_threshold_restore_defaults_resets_all_tuning_values(qtbot) -> None:
    from subsearch.io import toml_file
    from subsearch.ui.cards.search_cards import SearchThresholdCard
    from subsearch.ui.state.store import SettingsStore

    card = SearchThresholdCard(SettingsStore())
    qtbot.addWidget(card)
    session = toml_file.get_config_session()

    for row in card.tuning_rows.values():
        row.spin_box.setValue(1)
    assert session.read("search.token_weights.title") == 1

    card._restore_defaults()

    for token_name, default in DEFAULT_TOKEN_WEIGHTS.items():
        assert session.read(f"search.token_weights.{token_name}") == default
    for token_name, default in DEFAULT_TOKEN_MULTIPLIERS.items():
        assert session.read(f"search.token_multipliers.{token_name}") == default


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
    from subsearch.io import toml_file
    from subsearch.ui.cards.search_cards import SubtitleFiltersCard
    from subsearch.ui.state.store import SettingsStore

    store = SettingsStore()
    card = SubtitleFiltersCard(store)
    qtbot.addWidget(card)
    session = toml_file.get_config_session()

    for key in _SUBTITLE_FILTERS_DEFAULTS:
        store.write(key, not _SUBTITLE_FILTERS_DEFAULTS[key])

    card._restore_defaults()

    for key, default in _SUBTITLE_FILTERS_DEFAULTS.items():
        assert session.read(key) == default


def test_post_processing_restore_defaults(qtbot) -> None:
    from subsearch.io import toml_file
    from subsearch.ui.cards.post_processing_cards import PostProcessingCard
    from subsearch.ui.state.store import SettingsStore

    store = SettingsStore()
    card = PostProcessingCard(store)
    qtbot.addWidget(card)
    session = toml_file.get_config_session()

    store.write("post_processing.rename", False)
    store.write("post_processing.target_path", "custom/path")
    store.write("post_processing.path_resolution", "absolute")

    card._restore_defaults()

    for key, default in _POST_PROCESSING_DEFAULTS.items():
        assert session.read(key) == default


def test_notifications_restore_defaults(qtbot) -> None:
    from subsearch.io import toml_file
    from subsearch.ui.cards.system_cards import NotificationsCard
    from subsearch.ui.state.store import SettingsStore

    store = SettingsStore()
    card = NotificationsCard(store)
    qtbot.addWidget(card)
    session = toml_file.get_config_session()

    store.write("notifications.system_tray", False)
    store.write("notifications.summary_notification", True)

    card._restore_defaults()

    for key, default in _NOTIFICATIONS_DEFAULTS.items():
        assert session.read(key) == default


def test_download_manager_restore_defaults(qtbot) -> None:
    from subsearch.io import toml_file
    from subsearch.ui.cards.system_cards import DownloadManagerCard
    from subsearch.ui.state.store import SettingsStore

    store = SettingsStore()
    card = DownloadManagerCard(store)
    qtbot.addWidget(card)
    session = toml_file.get_config_session()

    store.write("download.automatic", False)
    store.write("download.open_manager_on_no_matches", False)

    card._restore_defaults()

    for key, default in _DOWNLOAD_MANAGER_DEFAULTS.items():
        assert session.read(key) == default


def test_application_restore_defaults(qtbot) -> None:
    from subsearch.io import toml_file
    from subsearch.ui.cards.system_cards import ApplicationCard
    from subsearch.ui.services.shell_integration import ShellIntegrationService
    from subsearch.ui.state.store import SettingsStore
    from subsearch.ui.state.tasks import TaskRunner

    store = SettingsStore()
    card = ApplicationCard(store, ShellIntegrationService(TaskRunner()))
    qtbot.addWidget(card)
    session = toml_file.get_config_session()

    store.write("application.show_terminal", True)
    store.write("application.single_instance", False)

    card._restore_defaults()

    for key, default in _APPLICATION_DEFAULTS.items():
        assert session.read(key) == default


def test_network_restore_defaults(qtbot) -> None:
    from subsearch.io import toml_file
    from subsearch.ui.cards.system_cards import NetworkCard
    from subsearch.ui.state.store import SettingsStore

    store = SettingsStore()
    card = NetworkCard(store)
    qtbot.addWidget(card)
    session = toml_file.get_config_session()

    store.write("network.api_call_limit", 99)
    store.write("network.request_connect_timeout", 99)
    store.write("network.request_read_timeout", 99)

    card._restore_defaults()

    for key, default in _NETWORK_DEFAULTS.items():
        assert session.read(key) == default
