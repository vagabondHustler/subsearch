import dataclasses

from subsearch.runtime.config import shell_integration


def test_changed_value_names_reports_only_differences():
    desired = {"subsearch": "Subsearch", "icon": "icon.ico", "command": "run"}
    current = {"subsearch": "Subsearch", "icon": "old.ico", "command": None}

    assert shell_integration.changed_value_names(desired, current) == ["icon", "command"]


def test_changed_value_names_empty_when_registry_matches():
    desired = {"subsearch": "Subsearch", "icon": ""}
    current = {"subsearch": "Subsearch", "icon": ""}

    assert shell_integration.changed_value_names(desired, current) == []


def test_changed_value_names_reports_everything_when_keys_absent():
    desired = {"subsearch": "Subsearch", "icon": "icon.ico"}
    current = {"subsearch": None, "icon": None}

    assert shell_integration.changed_value_names(desired, current) == ["subsearch", "icon"]


def test_reconcile_writes_in_executable_mode(monkeypatch):
    monkeypatch.setattr(
        shell_integration, "DEVICE_INFO", dataclasses.replace(shell_integration.DEVICE_INFO, mode="executable")
    )
    monkeypatch.setattr(shell_integration, "context_menu_enabled", lambda: True)
    monkeypatch.setattr(shell_integration, "desired_registry_values", lambda: {"command": "run"})
    monkeypatch.setattr(shell_integration, "current_registry_values", lambda: {"command": None})
    monkeypatch.setattr(shell_integration.windows_registry, "create_context_menu_keys", lambda: None)
    written = []
    monkeypatch.setattr(
        shell_integration.windows_registry,
        "write_registry_value",
        lambda sub_key, value_name, value: written.append((sub_key, value_name, value)),
    )

    shell_integration.reconcile_shell_integration()

    assert written == [(*shell_integration.VALUE_LOCATIONS["command"], "run")]


def test_reconcile_disabled_and_absent_does_not_touch_registry(monkeypatch):
    monkeypatch.setattr(shell_integration, "context_menu_enabled", lambda: False)
    monkeypatch.setattr(shell_integration.windows_registry, "context_menu_key_exists", lambda: False)
    monkeypatch.setattr(
        shell_integration.windows_registry,
        "del_context_menu",
        lambda: (_ for _ in ()).throw(AssertionError("deleted keys")),
    )

    shell_integration.reconcile_shell_integration()


def test_reconcile_disabled_and_present_deletes_keys(monkeypatch):
    monkeypatch.setattr(shell_integration, "context_menu_enabled", lambda: False)
    monkeypatch.setattr(shell_integration.windows_registry, "context_menu_key_exists", lambda: True)
    deleted = []
    monkeypatch.setattr(shell_integration.windows_registry, "del_context_menu", lambda: deleted.append(True))

    shell_integration.reconcile_shell_integration()

    assert deleted == [True]


def test_reconcile_enabled_and_up_to_date_writes_nothing(monkeypatch):
    desired = {"subsearch": "Subsearch", "icon": "", "appliesto": '".mkv"', "command": "run"}
    monkeypatch.setattr(shell_integration, "context_menu_enabled", lambda: True)
    monkeypatch.setattr(shell_integration, "desired_registry_values", lambda: desired)
    monkeypatch.setattr(shell_integration, "current_registry_values", lambda: dict(desired))
    monkeypatch.setattr(
        shell_integration.windows_registry,
        "create_context_menu_keys",
        lambda: (_ for _ in ()).throw(AssertionError("wrote keys")),
    )

    shell_integration.reconcile_shell_integration()


def test_reconcile_enabled_writes_only_stale_values(monkeypatch):
    desired = {"subsearch": "Subsearch", "icon": "icon.ico", "appliesto": '".mkv"', "command": "run"}
    current = {"subsearch": "Subsearch", "icon": "icon.ico", "appliesto": '".mkv"', "command": "old-run"}
    monkeypatch.setattr(shell_integration, "context_menu_enabled", lambda: True)
    monkeypatch.setattr(shell_integration, "desired_registry_values", lambda: desired)
    monkeypatch.setattr(shell_integration, "current_registry_values", lambda: current)
    monkeypatch.setattr(shell_integration.windows_registry, "create_context_menu_keys", lambda: None)
    written = []
    monkeypatch.setattr(
        shell_integration.windows_registry,
        "write_registry_value",
        lambda sub_key, value_name, value: written.append((sub_key, value_name, value)),
    )

    shell_integration.reconcile_shell_integration()

    assert written == [(shell_integration.REGISTRY_PATHS.subsearch_command, "", "run")]
