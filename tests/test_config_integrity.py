import json

from subsearch.io import json_file
from subsearch.io.nested_dict import get_keys_recursively
from subsearch.runtime.config import composition, defaults, integrity


def write_config(path, data):
    with path.open("w") as file:
        json.dump(data, file)


def test_resolve_restores_backup_when_config_is_corrupt(fake_config_file):
    composition.FILE_PATHS.config = fake_config_file
    backup_file = fake_config_file.with_suffix(f"{fake_config_file.suffix}.bak")

    good_config = defaults.get_default_app_config()
    good_config["search"]["accept_threshold"] = 73
    write_config(backup_file, good_config)
    fake_config_file.write_text("this is not valid json {")

    integrity.resolve_on_integrity_failure()

    assert json_file.load_json_value(fake_config_file, "search.accept_threshold") == 73
    assert not backup_file.exists()


def test_resolve_resets_to_default_when_corrupt_and_no_backup(fake_config_file):
    composition.FILE_PATHS.config = fake_config_file
    fake_config_file.write_text("this is not valid json {")

    integrity.resolve_on_integrity_failure()

    valid_keys = get_keys_recursively(composition.DEFAULT_CONFIG)
    config_keys = get_keys_recursively(json_file.load_json_data(fake_config_file))
    assert sorted(config_keys) == sorted(valid_keys)


def test_resolve_creates_default_when_missing(fake_config_file):
    composition.FILE_PATHS.config = fake_config_file
    fake_config_file.unlink()

    integrity.resolve_on_integrity_failure()

    assert fake_config_file.exists()
    valid_keys = get_keys_recursively(composition.DEFAULT_CONFIG)
    config_keys = get_keys_recursively(json_file.load_json_data(fake_config_file))
    assert sorted(config_keys) == sorted(valid_keys)


def test_repair_adds_missing_and_removes_obsolete_keys_in_one_write(fake_config_file):
    composition.FILE_PATHS.config = fake_config_file

    data = defaults.get_default_app_config()
    data["search"].pop("accept_threshold")
    data["obsolete_section"] = {"stale": True}
    write_config(fake_config_file, data)

    integrity.resolve_on_integrity_failure()

    repaired = json_file.load_json_data(fake_config_file)
    assert "accept_threshold" in repaired["search"]
    assert "obsolete_section" not in repaired
    valid_keys = get_keys_recursively(composition.DEFAULT_CONFIG)
    config_keys = get_keys_recursively(repaired)
    assert sorted(config_keys) == sorted(valid_keys)


def test_resolve_marks_fresh_when_config_missing(fake_config_file):
    composition.FILE_PATHS.config = fake_config_file
    fake_config_file.unlink()

    resolution = integrity.resolve_on_integrity_failure()

    assert resolution.is_fresh is True


def test_resolve_marks_fresh_when_repaired(fake_config_file):
    composition.FILE_PATHS.config = fake_config_file
    data = defaults.get_default_app_config()
    data["search"].pop("accept_threshold")
    write_config(fake_config_file, data)

    resolution = integrity.resolve_on_integrity_failure()

    assert resolution.is_fresh is True


def test_resolve_not_fresh_when_config_is_healthy(fake_config_file):
    composition.FILE_PATHS.config = fake_config_file
    write_config(fake_config_file, defaults.get_default_app_config())

    resolution = integrity.resolve_on_integrity_failure()

    assert resolution.is_fresh is False


def test_stale_temp_and_backup_removed_when_config_is_healthy(fake_config_file):
    composition.FILE_PATHS.config = fake_config_file
    temp_file = fake_config_file.with_suffix(f"{fake_config_file.suffix}.tmp")
    backup_file = fake_config_file.with_suffix(f"{fake_config_file.suffix}.bak")
    temp_file.write_text("leftover")
    write_config(backup_file, defaults.get_default_app_config())

    integrity.resolve_on_integrity_failure()

    assert not temp_file.exists()
    assert not backup_file.exists()
