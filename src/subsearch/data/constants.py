from subsearch.utils import io_app

DEVICE_INFO = io_app.get_system_info()
VIDEO_FILE = io_app.get_video_file_data()
APP_PATHS = io_app.get_app_paths()
FILE_PATHS = io_app.get_file_paths()
SUPPORTED_FILE_EXT = io_app.get_supported_file_ext()
SUPPORTED_PROVIDERS = io_app.get_supported_providers()
DEFAULT_CONFIG = io_app.get_default_app_config()
REGISTRY_PATHS = io_app.get_windows_registry_paths()
COMPUTER_NAME = io_app.get_computer_name()
