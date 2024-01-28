import importlib
import sys
from pathlib import Path

import pytest
import toml

from subsearch.globals import constants
from subsearch.globals import app_config


@pytest.fixture(scope="session")
def subsearch_app_path():
    app_path = Path(__file__).parent.parent / "src"
    sys.path.insert(0, str(app_path))
    return app_path


@pytest.fixture(scope="session")
def cwd():
    cwd = Path.cwd() / "src"
    sys.path.insert(0, str(cwd))
    return cwd


@pytest.fixture(scope="session")
def tests_path():
    tests_path = Path(__file__).parent
    sys.path.insert(0, str(tests_path))
    return tests_path


@pytest.fixture
def fake_language_data_file(tmp_path):
    fake_data = {
        "english": {"name": "English", "alpha_1": "en", "alpha_2b": "eng", "incompatibility": [], "subscene_id": 13}
    }

    fake_file = tmp_path / "fake_language_datag.toml"
    with fake_file.open("w") as f:
        toml.dump(fake_data, f)
    return fake_file


@pytest.fixture
def fake_config_file(tmp_path):
    fake_data = app_config.get_default_app_config()
    fake_file = tmp_path / "fake_subsearch_config.toml"
    with fake_file.open("w") as f:
        toml.dump(fake_data, f)

    return fake_file


@pytest.fixture
def fake_log_file(tmp_path):
    fake_file = tmp_path / "fake_subsearch_log.log"
    fake_file.touch()
    return fake_file


@pytest.fixture(autouse=True)
def override_constants(fake_language_data_file, fake_config_file, fake_log_file):
    app_config.DEVICE_INFO = app_config.get_system_info()
    app_config.VIDEO_FILE = app_config.get_video_file_data()
    app_config.APP_PATHS = app_config.get_app_paths()
    app_config.FILE_PATHS = app_config.get_file_paths()
    app_config.SUPPORTED_FILE_EXT = app_config.get_supported_file_ext()
    app_config.SUPPORTED_PROVIDERS = app_config.get_supported_providers()
    constants.FILE_PATHS.config = fake_config_file
    constants.FILE_PATHS.language_data = fake_language_data_file
    constants.FILE_PATHS.log = fake_log_file


@pytest.fixture(autouse=True)
def reset_constants():
    importlib.reload(app_config)
