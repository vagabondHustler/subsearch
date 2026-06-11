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


_APPLICATION_DEFAULTS = {
    "application.show_terminal": False,
    "application.single_instance": True,
}

_NETWORK_DEFAULTS = {
    "network.api_call_limit": 4,
    "network.request_connect_timeout": 4,
    "network.request_read_timeout": 5,
}


def _collect_switch_rows(card):
    from subsearch.ui.widgets.setting_rows import SwitchRow

    return {row.config_key: row for row in card.findChildren(SwitchRow)}


def _collect_spinbox_rows(card):
    from subsearch.ui.widgets.setting_rows import SpinBoxRow

    return {row.config_key: row for row in card.findChildren(SpinBoxRow)}


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

    store = SettingsStore()
    card = SearchThresholdCard(store)
    qtbot.addWidget(card)
    session = toml_file.get_config_session()

    store.write("search.accept_threshold", 50)
    for row in card.tuning_rows.values():
        row.spin_box.setValue(1)
    assert session.read("search.token_weights.title") == 1
    assert card.slider.value() == 50

    card._restore_defaults()

    assert card.slider.value() == 90
    for token_name, default in DEFAULT_TOKEN_WEIGHTS.items():
        assert session.read(f"search.token_weights.{token_name}") == default
        assert card.tuning_rows[token_name].spin_box.value() == default
    for token_name, default in DEFAULT_TOKEN_MULTIPLIERS.items():
        assert session.read(f"search.token_multipliers.{token_name}") == default
        assert card.tuning_rows[token_name].spin_box.value() == default


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
    switch_rows = _collect_switch_rows(card)

    for key, default in _SUBTITLE_FILTERS_DEFAULTS.items():
        store.write(key, not default)
    for key, default in _SUBTITLE_FILTERS_DEFAULTS.items():
        assert switch_rows[key].switch.isChecked() == (not default)

    card._restore_defaults()

    for key, default in _SUBTITLE_FILTERS_DEFAULTS.items():
        assert session.read(key) == default
        assert switch_rows[key].switch.isChecked() == default


def test_post_processing_restore_defaults(qtbot) -> None:
    from subsearch.io import toml_file
    from subsearch.ui.cards.post_processing_cards import PostProcessingCard
    from subsearch.ui.state.store import SettingsStore

    store = SettingsStore()
    card = PostProcessingCard(store)
    qtbot.addWidget(card)
    session = toml_file.get_config_session()
    switch_rows = _collect_switch_rows(card)

    store.write("post_processing.rename", False)
    store.write("post_processing.move_best", False)
    store.write("post_processing.create_missing_folder", False)
    assert switch_rows["post_processing.rename"].switch.isChecked() is False
    assert switch_rows["post_processing.move_best"].switch.isChecked() is False

    card._restore_defaults()

    for key, default in _POST_PROCESSING_DEFAULTS.items():
        assert session.read(key) == default
    assert switch_rows["post_processing.rename"].switch.isChecked() is True
    assert switch_rows["post_processing.move_best"].switch.isChecked() is True
    assert switch_rows["post_processing.create_missing_folder"].switch.isChecked() is True


def test_post_processing_restore_re_enables_destination(qtbot) -> None:
    from subsearch.ui.cards.post_processing_cards import PostProcessingCard
    from subsearch.ui.state.store import SettingsStore

    store = SettingsStore()
    card = PostProcessingCard(store)
    qtbot.addWidget(card)

    # Disable both move switches so the destination section becomes disabled.
    store.write("post_processing.move_best", False)
    store.write("post_processing.move_all", False)
    assert not card.destination.isEnabled()

    card._restore_defaults()

    # Default has move_best=True, so destination must be re-enabled after restore.
    assert card.destination.isEnabled()


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
    from subsearch.io import toml_file
    from subsearch.ui.cards.system_cards import NotificationsCard
    from subsearch.ui.state.store import SettingsStore

    store = SettingsStore()
    card = NotificationsCard(store)
    qtbot.addWidget(card)
    session = toml_file.get_config_session()
    switch_rows = _collect_switch_rows(card)

    store.write("notifications.system_tray", False)
    store.write("notifications.summary_notification", True)
    assert switch_rows["notifications.system_tray"].switch.isChecked() is False
    assert switch_rows["notifications.summary_notification"].switch.isChecked() is True

    card._restore_defaults()

    for key, default in _NOTIFICATIONS_DEFAULTS.items():
        assert session.read(key) == default
        assert switch_rows[key].switch.isChecked() == default


def test_download_manager_restore_defaults(qtbot) -> None:
    from subsearch.io import toml_file
    from subsearch.ui.cards.download_manager import DownloadManagerSettingsCard
    from subsearch.ui.services.video_file import VideoFileService
    from subsearch.ui.state.store import SettingsStore
    from subsearch.ui.widgets.setting_rows import SearchableComboBoxRow

    store = SettingsStore()
    card = DownloadManagerSettingsCard(store, VideoFileService())
    qtbot.addWidget(card)
    session = toml_file.get_config_session()
    combo_rows = {row.config_key: row for row in card.findChildren(SearchableComboBoxRow)}

    store.write("download_manager.search_mode", "manual")
    assert combo_rows["download_manager.search_mode"].combo_box.currentText() == "Manual"

    card._restore_defaults()

    assert session.read("download_manager.search_mode") == "hybrid"


def test_post_processing_card_disables_body_when_manually_handle_enabled(qtbot) -> None:
    from subsearch.ui.cards.post_processing_cards import PostProcessingCard
    from subsearch.ui.state.store import SettingsStore

    store = SettingsStore()
    card = PostProcessingCard(store)
    qtbot.addWidget(card)

    assert card.view.isEnabled()

    store.write("download_manager.manually_handle_post_processing", True)
    assert not card.view.isEnabled()
    assert card.isEnabled()

    store.write("download_manager.manually_handle_post_processing", False)
    assert card.view.isEnabled()


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
    from subsearch.io import toml_file
    from subsearch.ui.cards.system_cards import NetworkCard
    from subsearch.ui.state.store import SettingsStore

    store = SettingsStore()
    card = NetworkCard(store)
    qtbot.addWidget(card)
    session = toml_file.get_config_session()
    spinbox_rows = _collect_spinbox_rows(card)

    store.write("network.api_call_limit", 99)
    store.write("network.request_connect_timeout", 99)
    store.write("network.request_read_timeout", 99)
    assert spinbox_rows["network.api_call_limit"].spin_box.value() == 99
    assert spinbox_rows["network.request_connect_timeout"].spin_box.value() == 99
    assert spinbox_rows["network.request_read_timeout"].spin_box.value() == 99

    card._restore_defaults()

    for key, default in _NETWORK_DEFAULTS.items():
        assert session.read(key) == default
        assert spinbox_rows[key].spin_box.value() == default
