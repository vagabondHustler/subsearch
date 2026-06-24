from typing import Any

from subsearch.runtime.config.defaults import ConfigKey
from subsearch.runtime.config.nested_dict import read_nested_value
from subsearch.runtime.models import AppConfig


def get_app_config_from_data(data: dict[str, Any]) -> AppConfig:
    def value(key: ConfigKey) -> Any:
        return read_nested_value(data, key)

    return AppConfig(
        selected_language=value(ConfigKey.LANGUAGE_SELECTED),
        accept_threshold=value(ConfigKey.SEARCH_ACCEPT_THRESHOLD),
        hearing_impaired=value(ConfigKey.SEARCH_HEARING_IMPAIRED),
        non_hearing_impaired=value(ConfigKey.SEARCH_NON_HEARING_IMPAIRED),
        only_foreign_parts=value(ConfigKey.SEARCH_ONLY_FOREIGN_PARTS),
        providers=value(ConfigKey.SEARCH_PROVIDERS),
        downloads_per_provider=value(ConfigKey.SEARCH_DOWNLOADS_PER_PROVIDER),
        token_weights=value(ConfigKey.SEARCH_TOKEN_WEIGHTS),
        token_multipliers=value(ConfigKey.SEARCH_TOKEN_MULTIPLIERS),
        context_menu=value(ConfigKey.SHELL_INTEGRATION_CONTEXT_MENU),
        context_menu_icon=value(ConfigKey.SHELL_INTEGRATION_CONTEXT_MENU_ICON),
        file_extensions=value(ConfigKey.SHELL_INTEGRATION_FILE_EXTENSIONS),
        system_tray=value(ConfigKey.NOTIFICATIONS_SYSTEM_TRAY),
        notification_display_duration=value(ConfigKey.NOTIFICATIONS_DISPLAY_DURATION),
        notification_play_sound=value(ConfigKey.NOTIFICATIONS_PLAY_SOUND),
        search_mode=value(ConfigKey.SUBTITLE_WORKSPACE_SEARCH_MODE),
        subtitle_workspace_manual_post_processing=value(ConfigKey.SUBTITLE_WORKSPACE_MANUAL_POST_PROCESSING),
        post_processing=value(ConfigKey.POST_PROCESSING),
        paths=value(ConfigKey.PATHS),
        show_terminal=value(ConfigKey.APPLICATION_SHOW_TERMINAL),
        show_tray_icon=value(ConfigKey.APPLICATION_SHOW_TRAY_ICON),
        single_instance=value(ConfigKey.APPLICATION_SINGLE_INSTANCE),
        request_connect_timeout=value(ConfigKey.NETWORK_REQUEST_CONNECT_TIMEOUT),
        request_read_timeout=value(ConfigKey.NETWORK_REQUEST_READ_TIMEOUT),
        diagnostics=value(ConfigKey.DIAGNOSTICS),
        subsource_api_key_exists=value(ConfigKey.CREDENTIALS_SUBSOURCE_API_KEY_EXISTS),
        subsource_api_key=value(ConfigKey.CREDENTIALS_SUBSOURCE_API_KEY),
    )
