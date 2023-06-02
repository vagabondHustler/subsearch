from subsearch.data import app_paths
from subsearch.utils import file_manager, io_json


def extract_dict_keys(dictionary, keys=[]) -> list:
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


def update_config_file() -> None:
    """
    Updates the application's configuration file to match the desired config,
    preserving existing values.

    Returns:
        None.
    """
    if not io_json.APPCON_JSON.exists():
        return

    config_dict = io_json.retrieve_application_config()
    json_data = io_json.get_json_data()

    keys_to_remove = []
    for key in json_data:
        if key not in config_dict:
            keys_to_remove.append(key)

    for key in keys_to_remove:
        json_data.pop(key)

    keys_to_add = []
    for key in config_dict:
        if key not in json_data:
            keys_to_add.append(key)

    for key in keys_to_add:
        json_data[key] = config_dict[key]

    io_json.set_json_data(json_data)


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


def resolve_on_integrity_failure() -> None:
    """
    Resolves the application's configuration directory if the integrity check fails.
    Deletes everything in the directory, even if the update operation fails.

    Returns:
        None.
    """
    if not check_config_integrity() and app_paths.appdata_local.exists():
        try:
            update_config_file()
        except Exception:
            file_manager.del_directory(app_paths.appdata_local)


def initialize_application() -> None:
    """
    Initializes the application by performing necessary checks and setup.

    Returns:
        None.
    """
    resolve_on_integrity_failure()
    file_manager.create_directory(app_paths.tmpdir)
    file_manager.create_directory(app_paths.appdata_local)
    io_json.create_config_file()
