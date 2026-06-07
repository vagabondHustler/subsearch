from subsearch.runtime.config import factories, static_values

DEVICE_INFO = factories.get_system_info()
VIDEO_FILE = factories.get_video_file_data()
APP_PATHS = factories.get_app_paths()
FILE_PATHS = factories.get_file_paths()
SUPPORTED_FILE_EXT = static_values.SUPPORTED_FILE_EXTENSIONS
SUPPORTED_PROVIDERS = static_values.SUPPORTED_PROVIDERS
DEFAULT_CONFIG = factories.get_default_app_config()
REGISTRY_PATHS = factories.get_windows_registry_paths()
COMPUTER_NAME = static_values.COMPUTER_NAME
VERSION = static_values.APP_VERSION
GUID = static_values.APP_GUID
