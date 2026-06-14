from subsearch.runtime.config import defaults, metadata, paths, video_file

DEVICE_INFO = metadata.get_system_info()
VIDEO_FILE = video_file.get_video_file_data()
VIDEO_FILE_RESOLVER = video_file.VideoFileResolver(defaults.SUPPORTED_FILE_EXTENSIONS)
APP_PATHS = paths.get_app_paths()
FILE_PATHS = paths.get_file_paths()
SUPPORTED_FILE_EXT = defaults.SUPPORTED_FILE_EXTENSIONS
SUPPORTED_PROVIDERS = defaults.SUPPORTED_PROVIDERS
DEFAULT_CONFIG = defaults.get_default_app_config()
REGISTRY_PATHS = metadata.get_windows_registry_paths()
COMPUTER_NAME = metadata.COMPUTER_NAME
VERSION = metadata.APP_VERSION
GUID = metadata.APP_GUID
