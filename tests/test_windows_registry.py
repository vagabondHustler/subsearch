import dataclasses

from subsearch.io import windows_registry


def test_changed_value_names_reports_only_differences():
    desired = {"subsearch": "Subsearch", "icon": "icon.ico", "command": "run"}
    current = {"subsearch": "Subsearch", "icon": "old.ico", "command": None}

    assert windows_registry.changed_value_names(desired, current) == ["icon", "command"]


def test_changed_value_names_empty_when_registry_matches():
    desired = {"subsearch": "Subsearch", "icon": ""}
    current = {"subsearch": "Subsearch", "icon": ""}

    assert windows_registry.changed_value_names(desired, current) == []


def test_changed_value_names_reports_everything_when_keys_absent():
    desired = {"subsearch": "Subsearch", "icon": "icon.ico"}
    current = {"subsearch": None, "icon": None}

    assert windows_registry.changed_value_names(desired, current) == ["subsearch", "icon"]


def test_reconcile_skips_in_executable_mode(monkeypatch):
    monkeypatch.setattr(
        windows_registry, "DEVICE_INFO", dataclasses.replace(windows_registry.DEVICE_INFO, mode="executable")
    )
    monkeypatch.setattr(
        windows_registry, "current_registry_values", lambda: (_ for _ in ()).throw(AssertionError("touched registry"))
    )

    windows_registry.reconcile_shell_integration()


def test_reconcile_disabled_and_absent_does_not_touch_registry(monkeypatch):
    monkeypatch.setattr(
        windows_registry, "DEVICE_INFO", dataclasses.replace(windows_registry.DEVICE_INFO, mode="interpreter")
    )
    monkeypatch.setattr(windows_registry.config_session, "read_config_value", lambda key: False)
    monkeypatch.setattr(windows_registry, "_context_menu_key_exists", lambda: False)
    monkeypatch.setattr(
        windows_registry, "_del_context_menu", lambda: (_ for _ in ()).throw(AssertionError("deleted keys"))
    )

    windows_registry.reconcile_shell_integration()


def test_reconcile_disabled_and_present_deletes_keys(monkeypatch):
    monkeypatch.setattr(
        windows_registry, "DEVICE_INFO", dataclasses.replace(windows_registry.DEVICE_INFO, mode="interpreter")
    )
    monkeypatch.setattr(windows_registry.config_session, "read_config_value", lambda key: False)
    monkeypatch.setattr(windows_registry, "_context_menu_key_exists", lambda: True)
    deleted = []
    monkeypatch.setattr(windows_registry, "_del_context_menu", lambda: deleted.append(True))

    windows_registry.reconcile_shell_integration()

    assert deleted == [True]


def test_reconcile_enabled_and_up_to_date_writes_nothing(monkeypatch):
    desired = {"subsearch": "Subsearch", "icon": "", "appliesto": '".mkv"', "command": "run"}
    monkeypatch.setattr(
        windows_registry, "DEVICE_INFO", dataclasses.replace(windows_registry.DEVICE_INFO, mode="interpreter")
    )
    monkeypatch.setattr(windows_registry.config_session, "read_config_value", lambda key: True)
    monkeypatch.setattr(windows_registry, "desired_registry_values", lambda: desired)
    monkeypatch.setattr(windows_registry, "current_registry_values", lambda: dict(desired))
    monkeypatch.setattr(
        windows_registry, "_create_context_menu_keys", lambda: (_ for _ in ()).throw(AssertionError("wrote keys"))
    )

    windows_registry.reconcile_shell_integration()


def test_reconcile_enabled_writes_only_stale_values(monkeypatch):
    desired = {"subsearch": "Subsearch", "icon": "icon.ico", "appliesto": '".mkv"', "command": "run"}
    current = {"subsearch": "Subsearch", "icon": "icon.ico", "appliesto": '".mkv"', "command": "old-run"}
    monkeypatch.setattr(
        windows_registry, "DEVICE_INFO", dataclasses.replace(windows_registry.DEVICE_INFO, mode="interpreter")
    )
    monkeypatch.setattr(windows_registry.config_session, "read_config_value", lambda key: True)
    monkeypatch.setattr(windows_registry, "desired_registry_values", lambda: desired)
    monkeypatch.setattr(windows_registry, "current_registry_values", lambda: current)
    monkeypatch.setattr(windows_registry, "_create_context_menu_keys", lambda: None)
    written = []
    monkeypatch.setattr(
        windows_registry,
        "_write_registry_value",
        lambda sub_key, value_name, value: written.append((sub_key, value_name, value)),
    )

    windows_registry.reconcile_shell_integration()

    assert written == [(windows_registry.REGISTRY_PATHS.subsearch_command, "", "run")]
