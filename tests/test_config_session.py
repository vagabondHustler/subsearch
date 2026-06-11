from subsearch.io import toml_file
from subsearch.runtime.config import config_session


def test_session_keeps_disk_untouched_until_commit(fake_config_file):
    session = config_session.ConfigSession(fake_config_file, toml_file.load_toml_data(fake_config_file))

    session.write("search.accept_threshold", 42)

    assert session.read("search.accept_threshold") == 42
    assert toml_file.load_toml_value(fake_config_file, "search.accept_threshold") == 90


def test_session_commit_persists_and_clears_backup(fake_config_file):
    backup_file = fake_config_file.with_suffix(f"{fake_config_file.suffix}.bak")
    session = config_session.ConfigSession(fake_config_file, toml_file.load_toml_data(fake_config_file))

    session.write("search.accept_threshold", 42)
    assert backup_file.exists()

    session.commit()

    assert toml_file.load_toml_value(fake_config_file, "search.accept_threshold") == 42
    assert not backup_file.exists()


def test_session_backup_holds_last_known_good_before_first_write(fake_config_file):
    backup_file = fake_config_file.with_suffix(f"{fake_config_file.suffix}.bak")
    session = config_session.ConfigSession(fake_config_file, toml_file.load_toml_data(fake_config_file))

    session.write("search.accept_threshold", 1)
    session.write("search.accept_threshold", 2)

    assert toml_file.load_toml_value(backup_file, "search.accept_threshold") == 90


def test_session_revert_discards_uncommitted_changes(fake_config_file):
    session = config_session.ConfigSession(fake_config_file, toml_file.load_toml_data(fake_config_file))

    session.write("search.accept_threshold", 42)
    session.revert()

    assert session.read("search.accept_threshold") == 90


def test_snapshot_is_isolated_from_later_nested_mutations(fake_config_file):
    session = config_session.ConfigSession(fake_config_file, toml_file.load_toml_data(fake_config_file))

    snapshot = session.snapshot()
    original_move_best = snapshot.post_processing["move_best"]

    session.write("post_processing.move_best", not original_move_best)

    assert snapshot.post_processing["move_best"] == original_move_best


def test_snapshot_is_isolated_from_later_provider_mutations(fake_config_file):
    session = config_session.ConfigSession(fake_config_file, toml_file.load_toml_data(fake_config_file))

    snapshot = session.snapshot()
    a_provider = next(iter(snapshot.providers))
    original = snapshot.providers[a_provider]

    session.in_memory_data["search"]["providers"][a_provider] = not original

    assert snapshot.providers[a_provider] == original


def test_later_snapshot_reflects_change_earlier_snapshot_does_not(fake_config_file):
    session = config_session.ConfigSession(fake_config_file, toml_file.load_toml_data(fake_config_file))

    before = session.snapshot()
    session.write("search.accept_threshold", 42)
    after = session.snapshot()

    assert before.accept_threshold == 90
    assert after.accept_threshold == 42


def test_uncommitted_edit_does_not_survive_simulated_crash(fake_config_file):
    session = config_session.ConfigSession(fake_config_file, toml_file.load_toml_data(fake_config_file))

    session.write("search.accept_threshold", 42)

    fresh_disk_value = toml_file.load_toml_value(fake_config_file, "search.accept_threshold")
    assert fresh_disk_value == 90
