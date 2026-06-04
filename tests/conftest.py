import importlib
import sys
from pathlib import Path
from typing import Any

import pytest
import toml

from subsearch.runtime import constants
from subsearch.runtime import factories


@pytest.fixture(scope="session")
def subsearch_app_path() -> Path:
    app_path = Path(__file__).parent.parent / "src"
    sys.path.insert(0, str(app_path))
    return app_path


@pytest.fixture(scope="session")
def cwd() -> Path:
    cwd = Path.cwd() / "src"
    sys.path.insert(0, str(cwd))
    return cwd


@pytest.fixture(scope="session")
def tests_path() -> Path:
    tests_path = Path(__file__).parent
    sys.path.insert(0, str(tests_path))
    return tests_path


@pytest.fixture
def fake_language_data_file(tmp_path) -> Any:
    fake_data = {"english": {"name": "English", "two_letter_code": "en", "three_letter_code": "eng", "incompatibility": []}}

    fake_file = tmp_path / "fake_language_datag.toml"
    with fake_file.open("w") as f:
        toml.dump(fake_data, f)
    return fake_file


@pytest.fixture
def fake_config_file(tmp_path) -> Any:
    fake_data = factories.get_default_app_config()
    fake_file = tmp_path / "fake_subsearch_config.toml"
    with fake_file.open("w") as f:
        toml.dump(fake_data, f)

    return fake_file


@pytest.fixture
def fake_log_file(tmp_path) -> Any:
    fake_file = tmp_path / "fake_subsearch_log.log"
    fake_file.touch()
    return fake_file


@pytest.fixture(autouse=True)
def override_constants(fake_language_data_file, fake_config_file, fake_log_file) -> None:
    constants.FILE_PATHS.config = fake_config_file
    constants.FILE_PATHS.subtitle_languages = fake_language_data_file
    constants.FILE_PATHS.log = fake_log_file


@pytest.fixture(autouse=True)
def reset_constants() -> None:
    importlib.reload(factories)


@pytest.fixture(autouse=True)
def reset_config_session() -> Any:
    from subsearch.io import toml_file

    toml_file.reset_config_session()
    yield
    toml_file.reset_config_session()
