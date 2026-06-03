from subsearch.runtime import factories, static_values

DEVICE_INFO = factories.get_system_info()
VIDEO_FILE = factories.get_video_file_data()
APP_PATHS = factories.get_app_paths()
FILE_PATHS = factories.get_file_paths()
SUPPORTED_FILE_EXT = static_values.get_supported_file_ext()
SUPPORTED_PROVIDERS = static_values.get_supported_providers()
DEFAULT_CONFIG = factories.get_default_app_config()
REGISTRY_PATHS = factories.get_windows_registry_paths()
COMPUTER_NAME = static_values.get_computer_name()
VERSION = static_values.get_app_version()
GUID = static_values.get_guid()
