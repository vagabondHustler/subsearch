from pathlib import Path

from subsearch.runtime.config import defaults, metadata, paths, search_subject
from subsearch.runtime.config.resolved_paths import PathResolver

DEVICE_INFO = metadata.get_system_info()
SEARCH_SUBJECT, WORKSPACE = search_subject.get_search_data()
SEARCH_RESOLVER = search_subject.SearchResolver(defaults.SUPPORTED_FILE_EXTENSIONS)
APP_PATHS = paths.get_app_paths()
PATH_RESOLVER = PathResolver(APP_PATHS.tmp_dir, Path.home() / "Downloads" / "subs")
FILE_PATHS = paths.get_file_paths()
SUPPORTED_FILE_EXT = defaults.SUPPORTED_FILE_EXTENSIONS
SUPPORTED_PROVIDERS = defaults.SUPPORTED_PROVIDERS
DEFAULT_CONFIG = defaults.get_default_app_config()
REGISTRY_PATHS = metadata.get_windows_registry_paths()
COMPUTER_NAME = metadata.COMPUTER_NAME
VERSION = metadata.APP_VERSION
GUID = metadata.APP_GUID
APP_USER_MODEL_ID = "Subsearch.Subsearch"
