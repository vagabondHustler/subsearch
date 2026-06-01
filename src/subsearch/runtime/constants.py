from subsearch.runtime import factories

DEVICE_INFO = factories.get_system_info()
VIDEO_FILE = factories.get_video_file_data()
APP_PATHS = factories.get_app_paths()
FILE_PATHS = factories.get_file_paths()
SUPPORTED_FILE_EXT = factories.get_supported_file_ext()
SUPPORTED_PROVIDERS = factories.get_supported_providers()
DEFAULT_CONFIG = factories.get_default_app_config()
REGISTRY_PATHS = factories.get_windows_registry_paths()
COMPUTER_NAME = factories.get_computer_name()
VERSION = factories.get_app_version()
GUID = factories.get_guid()
