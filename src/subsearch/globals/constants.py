from subsearch.globals import app_config

DEVICE_INFO = app_config.get_system_info()
VIDEO_FILE = app_config.get_video_file_data()
APP_PATHS = app_config.get_app_paths()
FILE_PATHS = app_config.get_file_paths()
SUPPORTED_FILE_EXT = app_config.get_supported_file_ext()
SUPPORTED_PROVIDERS = app_config.get_supported_providers()
DEFAULT_CONFIG = app_config.get_default_app_config()
REGISTRY_PATHS = app_config.get_windows_registry_paths()
COMPUTER_NAME = app_config.get_computer_name()
VERSION = app_config.get_app_version()
GUID = app_config.get_guid()
