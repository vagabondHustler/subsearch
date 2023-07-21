from subsearch.data.constants import APP_PATHS
from subsearch.utils import io_file_system, io_json


def check_config_integrity() -> bool:
    """
    Checks the integrity of the application's configuration file.

    Returns:
        bool: True if the configuration is intact, False otherwise.
    """
    if not APP_PATHS.application_config_json.exists():
        return False
    app_con_dict = io_json.extract_dict_keys(io_json.retrieve_application_config())
    app_con_json = io_json.extract_dict_keys(io_json.get_json_data())
    app_con_dict.sort()
    app_con_json.sort()
    return app_con_json == app_con_dict


def resolve_on_integrity_failure() -> None:
    """
    Resolves the application's configuration directory if the integrity check fails.
    Deletes everything in the directory, even if the update operation fails.

    Returns:
        None.
    """
    if not check_config_integrity() and APP_PATHS.app_data_local.exists():
        try:
            io_json.update_config_file()
        except Exception:
            io_file_system.del_directory_content(APP_PATHS.app_data_local)
