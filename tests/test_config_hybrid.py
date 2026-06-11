import pytest

from subsearch.core.bootstrap import Bootstrap
from subsearch.io import toml_file
from subsearch.io.toml_file import AppConfig
from subsearch.runtime.config.constants import FILE_PATHS


class MinimalBootstrap:
    app_config: AppConfig
    resync_app_config = Bootstrap.resync_app_config
    prevent_conflicting_config_settings = Bootstrap.prevent_conflicting_config_settings


@pytest.fixture
def bootstrap(fake_config_file) -> MinimalBootstrap:
    FILE_PATHS.config = fake_config_file
    toml_file.FILE_PATHS.config = fake_config_file
    instance = MinimalBootstrap()
    instance.app_config = toml_file.get_config_session().snapshot()
    return instance


def test_run_snapshot_is_frozen_against_mid_run_edits(bootstrap: MinimalBootstrap):
    original_threshold = bootstrap.app_config.accept_threshold

    toml_file.get_config_session().write("search.accept_threshold", original_threshold + 5)

    assert bootstrap.app_config.accept_threshold == original_threshold


def test_resync_picks_up_edits_made_in_the_manager(bootstrap: MinimalBootstrap):
    original_move_best = bootstrap.app_config.post_processing["move_best"]

    toml_file.get_config_session().write("post_processing.move_best", not original_move_best)
    bootstrap.resync_app_config()

    assert bootstrap.app_config.post_processing["move_best"] == (not original_move_best)


def test_resync_does_not_require_commit_to_be_visible(bootstrap: MinimalBootstrap):
    session = toml_file.get_config_session()
    session.write("search.accept_threshold", 33)

    bootstrap.resync_app_config()

    assert bootstrap.app_config.accept_threshold == 33
    assert toml_file.load_toml_value(FILE_PATHS.config, "search.accept_threshold") == 90


def test_conflict_resolver_resolves_move_best_move_all(bootstrap: MinimalBootstrap):
    session = toml_file.get_config_session()
    session.write("post_processing.move_best", True)
    session.write("post_processing.move_all", True)
    bootstrap.resync_app_config()

    bootstrap.prevent_conflicting_config_settings()

    assert bootstrap.app_config.post_processing["move_best"] is False
    assert toml_file.load_toml_value(FILE_PATHS.config, "post_processing.move_best") is False
