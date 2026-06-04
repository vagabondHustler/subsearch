import toml

from subsearch.io import toml_file
from subsearch.runtime import constants, factories


def write_config(path, data):
    with path.open("w") as file:
        toml.dump(data, file)


def test_dump_toml_data_is_atomic_and_leaves_no_temp_file(tmp_path):
    config_path = tmp_path / "config.toml"
    temp_path = tmp_path / "config.toml.tmp"

    toml_file.dump_toml_data(config_path, {"search": {"accept_threshold": 90}})

    assert config_path.exists()
    assert not temp_path.exists()
    assert toml_file.load_toml_data(config_path) == {"search": {"accept_threshold": 90}}


def test_nested_value_read_set_delete():
    data = {"search": {"accept_threshold": 90}}

    assert toml_file.read_nested_value(data, "search.accept_threshold") == 90

    toml_file.set_nested_value(data, "search.accept_threshold", 50)
    assert data["search"]["accept_threshold"] == 50

    toml_file.delete_nested_value(data, "search.accept_threshold")
    assert "accept_threshold" not in data["search"]


def test_delete_nested_value_with_missing_parent_does_not_raise():
    toml_file.delete_nested_value({}, "missing.parent.leaf")


def test_read_nested_value_with_missing_parent_returns_none():
    assert toml_file.read_nested_value({}, "missing.parent.leaf") is None


def test_session_keeps_disk_untouched_until_commit(fake_config_file):
    session = toml_file.ConfigSession(fake_config_file)

    session.write("search.accept_threshold", 42)

    assert session.read("search.accept_threshold") == 42
    assert toml_file.load_toml_value(fake_config_file, "search.accept_threshold") == 90


def test_session_commit_persists_and_clears_backup(fake_config_file):
    backup_file = fake_config_file.with_suffix(f"{fake_config_file.suffix}.bak")
    session = toml_file.ConfigSession(fake_config_file)

    session.write("search.accept_threshold", 42)
    assert backup_file.exists()

    session.commit()

    assert toml_file.load_toml_value(fake_config_file, "search.accept_threshold") == 42
    assert not backup_file.exists()


def test_session_backup_holds_last_known_good_before_first_write(fake_config_file):
    backup_file = fake_config_file.with_suffix(f"{fake_config_file.suffix}.bak")
    session = toml_file.ConfigSession(fake_config_file)

    session.write("search.accept_threshold", 1)
    session.write("search.accept_threshold", 2)

    assert toml_file.load_toml_value(backup_file, "search.accept_threshold") == 90


def test_session_revert_discards_uncommitted_changes(fake_config_file):
    session = toml_file.ConfigSession(fake_config_file)

    session.write("search.accept_threshold", 42)
    session.revert()

    assert session.read("search.accept_threshold") == 90


def test_snapshot_is_isolated_from_later_nested_mutations(fake_config_file):
    session = toml_file.ConfigSession(fake_config_file)

    snapshot = session.snapshot()
    original_move_best = snapshot.post_processing["move_best"]

    session.write("post_processing.move_best", not original_move_best)

    assert snapshot.post_processing["move_best"] == original_move_best


def test_snapshot_is_isolated_from_later_provider_mutations(fake_config_file):
    session = toml_file.ConfigSession(fake_config_file)

    snapshot = session.snapshot()
    a_provider = next(iter(snapshot.providers))
    original = snapshot.providers[a_provider]

    session.in_memory_data["search"]["providers"][a_provider] = not original

    assert snapshot.providers[a_provider] == original


def test_later_snapshot_reflects_change_earlier_snapshot_does_not(fake_config_file):
    session = toml_file.ConfigSession(fake_config_file)

    before = session.snapshot()
    session.write("search.accept_threshold", 42)
    after = session.snapshot()

    assert before.accept_threshold == 90
    assert after.accept_threshold == 42


def test_uncommitted_edit_does_not_survive_simulated_crash(fake_config_file):
    session = toml_file.ConfigSession(fake_config_file)

    session.write("search.accept_threshold", 42)

    fresh_disk_value = toml_file.load_toml_value(fake_config_file, "search.accept_threshold")
    assert fresh_disk_value == 90


def test_resolve_restores_backup_when_config_is_corrupt(fake_config_file):
    constants.FILE_PATHS.config = fake_config_file
    toml_file.FILE_PATHS.config = fake_config_file
    backup_file = fake_config_file.with_suffix(f"{fake_config_file.suffix}.bak")

    good_config = factories.get_default_app_config()
    good_config["search"]["accept_threshold"] = 73
    write_config(backup_file, good_config)
    fake_config_file.write_text("this is { not valid toml")

    toml_file.resolve_on_integrity_failure()

    assert toml_file.load_toml_value(fake_config_file, "search.accept_threshold") == 73
    assert not backup_file.exists()


def test_resolve_resets_to_default_when_corrupt_and_no_backup(fake_config_file):
    constants.FILE_PATHS.config = fake_config_file
    toml_file.FILE_PATHS.config = fake_config_file
    fake_config_file.write_text("this is { not valid toml")

    toml_file.resolve_on_integrity_failure()

    valid_keys = toml_file.get_keys_recursively(constants.DEFAULT_CONFIG)
    config_keys = toml_file.get_keys_recursively(toml_file.load_toml_data(fake_config_file))
    assert sorted(config_keys) == sorted(valid_keys)


def test_resolve_creates_default_when_missing(fake_config_file):
    constants.FILE_PATHS.config = fake_config_file
    toml_file.FILE_PATHS.config = fake_config_file
    fake_config_file.unlink()

    toml_file.resolve_on_integrity_failure()

    assert fake_config_file.exists()
    valid_keys = toml_file.get_keys_recursively(constants.DEFAULT_CONFIG)
    config_keys = toml_file.get_keys_recursively(toml_file.load_toml_data(fake_config_file))
    assert sorted(config_keys) == sorted(valid_keys)


def test_repair_adds_missing_and_removes_obsolete_keys_in_one_write(fake_config_file):
    constants.FILE_PATHS.config = fake_config_file
    toml_file.FILE_PATHS.config = fake_config_file

    data = factories.get_default_app_config()
    data["search"].pop("accept_threshold")
    data["obsolete_section"] = {"stale": True}
    write_config(fake_config_file, data)

    toml_file.resolve_on_integrity_failure()

    repaired = toml_file.load_toml_data(fake_config_file)
    assert "accept_threshold" in repaired["search"]
    assert "obsolete_section" not in repaired
    valid_keys = toml_file.get_keys_recursively(constants.DEFAULT_CONFIG)
    config_keys = toml_file.get_keys_recursively(repaired)
    assert sorted(config_keys) == sorted(valid_keys)


def test_stale_temp_and_backup_removed_when_config_is_healthy(fake_config_file):
    constants.FILE_PATHS.config = fake_config_file
    toml_file.FILE_PATHS.config = fake_config_file
    temp_file = fake_config_file.with_suffix(f"{fake_config_file.suffix}.tmp")
    backup_file = fake_config_file.with_suffix(f"{fake_config_file.suffix}.bak")
    temp_file.write_text("leftover")
    write_config(backup_file, factories.get_default_app_config())

    toml_file.resolve_on_integrity_failure()

    assert not temp_file.exists()
    assert not backup_file.exists()
