from enum import StrEnum


class CardKey(StrEnum):
    SUBTITLE_FILTERS = "card.subtitle_filters"
    SUBTITLE_HANDLING = "card.subtitle_handling"
    PATHS = "card.paths"
    SHELL_INTEGRATION = "card.shell_integration"
    NOTIFICATIONS = "card.notifications"
    APPLICATION = "card.application"
    NETWORK = "card.network"
    UPDATE = "card.update"
    RESOURCES = "card.resources"

    DIAGNOSTICS_HEADER = "diagnostics.header"
    AVAILABLE_SUBTITLES = "subtitle_workspace.available_subtitles"
    SUBSOURCE_API_KEY = "credentials.subsource_api_key"
    SUBSOURCE_REQUEST_LIMITS = "credentials.subsource_request_limits"
    SUBSOURCE_GETTING_API_KEY = "credentials.subsource_getting_api_key"
