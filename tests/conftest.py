import importlib
import sys
from pathlib import Path
from typing import Any

import pytest
import toml

from subsearch.globals import constants
from subsearch import bootstrap


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
    fake_data = {"english": {"name": "English", "alpha_1": "en", "alpha_2b": "eng", "incompatibility": []}}

    fake_file = tmp_path / "fake_language_datag.toml"
    with fake_file.open("w") as f:
        toml.dump(fake_data, f)
    return fake_file


@pytest.fixture
def fake_config_file(tmp_path) -> Any:
    fake_data = bootstrap.get_default_app_config()
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
    bootstrap.DEVICE_INFO = bootstrap.get_system_info()
    bootstrap.VIDEO_FILE = bootstrap.get_video_file_data()
    bootstrap.APP_PATHS = bootstrap.get_app_paths()
    bootstrap.FILE_PATHS = bootstrap.get_file_paths()
    bootstrap.FILE_EXTENSIONS = bootstrap.get_file_extensions()
    bootstrap.SUPPORTED_PROVIDERS = bootstrap.get_subtitle_providers()
    constants.FILE_PATHS.config = fake_config_file
    constants.FILE_PATHS.language_data = fake_language_data_file
    constants.FILE_PATHS.log = fake_log_file


@pytest.fixture(autouse=True)
def reset_constants() -> None:
    importlib.reload(bootstrap)
