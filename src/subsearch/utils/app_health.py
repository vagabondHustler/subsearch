from subsearch.data.constants import APP_PATHS, FILE_PATHS
from subsearch.utils import io_file_system, io_json


def check_config_integrity() -> bool:
    """
    Checks the integrity of the application's configuration file.

    Returns:
        bool: True if the configuration is intact, False otherwise.
    """
    if not FILE_PATHS.subsearch_config.exists():
        return False
    app_con_dict = io_json.extract_dict_keys(io_json.retrieve_application_config())
    subsearch_config = io_json.extract_dict_keys(io_json.get_json_data(FILE_PATHS.subsearch_config))
    app_con_dict.sort()
    subsearch_config.sort()
    return subsearch_config == app_con_dict


def resolve_on_integrity_failure() -> None:
    """
    Resolves the application's configuration directory if the integrity check fails.
    Deletes everything in the directory, even if the update operation fails.

    Returns:
        None.
    """
    if not check_config_integrity() and APP_PATHS.appdata_subsearch.exists():
        try:
            io_json.update_config_file()
        except Exception:
            io_file_system.del_directory_content(APP_PATHS.appdata_subsearch)
