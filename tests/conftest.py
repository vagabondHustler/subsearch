import importlib
import json
import sys
from pathlib import Path

import pytest

from subsearch.data import constants
from subsearch.utils import io_app


@pytest.fixture(scope="session")
def subsearch_app_path():
    """Fixture to get the path to the subsearch directory."""
    app_path = Path(__file__).parent.parent / "src"
    sys.path.insert(0, str(app_path))
    return app_path

@pytest.fixture(scope="session")
def cwd():
    """Fixture to get the path to the subsearch directory."""
    cwd = Path.cwd() / "src"
    sys.path.insert(0, str(cwd))
    return cwd

@pytest.fixture(scope="session")
def tests_path():
    """Fixture to get the path to the tests directory."""
    tests_path = Path(__file__).parent
    sys.path.insert(0, str(tests_path))
    return tests_path

@pytest.fixture
def fake_languages_config_file(tmp_path):
    fake_data = {
        "english": {"name": "English", "alpha_1": "en", "alpha_2b": "eng", "incompatibility": [], "subscene_id": 13}
    }

    fake_file = tmp_path / "fake_languages_config.json"
    with fake_file.open("w") as f:
        json.dump(fake_data, f)
    return fake_file


@pytest.fixture
def fake_subsearch_config_file(tmp_path):
    fake_data = {
        "current_language": "english",
        "subtitle_type": {"hearing_impaired": True, "non_hearing_impaired": True},
        "foreign_only": False,
        "percentage_threshold": 90,
        "autoload_rename": True,
        "autoload_move": True,
        "context_menu": True,
        "context_menu_icon": True,
        "system_tray": True,
        "toast_summary": False,
        "manual_download_on_fail": True,
        "use_threading": True,
        "multiple_app_instances": False,
        "show_terminal": False,
        "log_to_file": False,
        "file_extensions": {
            ".avi": True,
            ".mp4": True,
            ".mkv": True,
            ".mpg": True,
            ".mpeg": True,
            ".mov": True,
            ".rm": True,
            ".vob": True,
            ".wmv": True,
            ".flv": True,
            ".3gp": True,
            ".3g2": True,
            ".swf": True,
            ".mswmm": True,
        },
        "providers": {
            "opensubtitles_site": True,
            "opensubtitles_hash": True,
            "subscene_site": True,
            "yifysubtitles_site": True,
        },
    }
    fake_file = tmp_path / "fake_subsearch_config.json"
    with fake_file.open("w") as f:
        json.dump(fake_data, f)

    return fake_file


@pytest.fixture
def fake_subsearch_log_file(tmp_path):
    fake_file = tmp_path / "fake_subsearch_log.log"
    fake_file.touch()
    return fake_file


@pytest.fixture(autouse=True)
def override_constants(fake_languages_config_file, fake_subsearch_config_file, fake_subsearch_log_file):
    io_app.DEVICE_INFO = io_app.get_system_info()
    io_app.VIDEO_FILE = io_app.get_video_file_data()
    io_app.APP_PATHS = io_app.get_app_paths()
    io_app.FILE_PATHS = io_app.get_file_paths()
    io_app.SUPPORTED_FILE_EXT = io_app.get_supported_file_ext()
    io_app.SUPPORTED_PROVIDERS = io_app.get_supported_providers()
    constants.FILE_PATHS.subsearch_config = fake_subsearch_config_file
    constants.FILE_PATHS.languages_config = fake_languages_config_file
    constants.FILE_PATHS.subsearch_log = fake_subsearch_log_file


@pytest.fixture(autouse=True)
def reset_constants():
    # Reset the constants to their original values after testing
    importlib.reload(io_app)
