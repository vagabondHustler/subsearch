import pytest

from subsearch.runtime.config.static_values import (
    DEFAULT_TOKEN_MULTIPLIERS,
    DEFAULT_TOKEN_WEIGHTS,
)


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
