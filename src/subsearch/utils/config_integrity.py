from subsearch.data import app_paths
from subsearch.utils import file_manager, io_json


def extract_dict_keys(dictionary, keys=[]):
    """
    Extracts all keys from a nested dictionary.

    Args:
        dictionary (dict): The dictionary to extract keys from.
        keys (list, optional): The list of parent keys. Defaults to [].

    Returns:
        list: List of keys in the dictionary.
    """
    if keys is None:
        keys = []
    json_keys = []
    for key, value in dictionary.items():
        nested_keys = keys + [key]
        if isinstance(value, dict):
            json_keys.extend(extract_dict_keys(value, nested_keys))
        else:
            json_keys.append(".".join(nested_keys))
    return json_keys


def check_config_integrity() -> bool:
    """
    Checks the integrity of the application's configuration file.

    Returns:
        bool: True if the configuration is intact, False otherwise.
    """
    if not io_json.APPCON_JSON.exists():
        return False
    app_con_dict = extract_dict_keys(io_json.retrieve_application_config())
    app_con_json = extract_dict_keys(io_json.get_json_data())
    app_con_dict.sort()
    app_con_json.sort()
    return app_con_json == app_con_dict


def cleanup_on_integrity_failure():
    """
    Cleans up the application's configuration directory if the integrity check fails.

    Returns:
        None.
    """
    if not check_config_integrity() and app_paths.appdata_local.exists():
        file_manager.del_directory(app_paths.appdata_local)

