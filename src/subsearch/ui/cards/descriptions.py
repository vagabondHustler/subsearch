from dataclasses import dataclass
from enum import StrEnum

from subsearch.runtime.config.defaults import ConfigKey


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


@dataclass(frozen=True, slots=True)
class SettingDescription:
    title: str
    explanation: str


SETTING_DESCRIPTIONS: dict[ConfigKey | CardKey, SettingDescription] = {
    ConfigKey.LANGUAGE_SELECTED: SettingDescription(
        "Subtitle language",
        "The language you want subtitles in. Start typing to filter, then press Enter to pick.",
    ),
    ConfigKey.SEARCH_ACCEPT_THRESHOLD: SettingDescription(
        "Filename match threshold",
        "How close a subtitle's name must be to your video. Higher is stricter.",
    ),
    ConfigKey.SEARCH_TOKEN_WEIGHTS: SettingDescription(
        "Weights",
        "How much the title, source (BluRay, WEB), and release group count when scoring a match. "
        "Raise one to make it matter more.",
    ),
    ConfigKey.SEARCH_TOKEN_MULTIPLIERS: SettingDescription(
        "Mismatch multiplier",
        "How much to lower the score when a part is wrong (year, season, episode, edition). "
        "Lower rejects mismatches harder; 1.0 ignores them.",
    ),
    ConfigKey.SEARCH_HEARING_IMPAIRED: SettingDescription(
        "Hearing impaired",
        "Include subtitles that also describe sounds and who is speaking.",
    ),
    ConfigKey.SEARCH_NON_HEARING_IMPAIRED: SettingDescription(
        "Non-hearing impaired",
        "Include normal subtitles that show only the spoken words.",
    ),
    ConfigKey.SEARCH_ONLY_FOREIGN_PARTS: SettingDescription(
        "Foreign parts only",
        "Only get subtitles for the foreign-language parts, not the whole video.",
    ),
    ConfigKey.SEARCH_PROVIDERS: SettingDescription(
        "Subtitle providers",
        "The sites Subsearch searches. Turn one off to skip it. " "Greyed-out ones have no subtitles in {language}.",
    ),
    ConfigKey.SHELL_INTEGRATION_CONTEXT_MENU: SettingDescription(
        "Context menu",
        "Add Subsearch to the right-click menu for video files.",
    ),
    ConfigKey.SHELL_INTEGRATION_CONTEXT_MENU_ICON: SettingDescription(
        "Context menu icon",
        "Show the Subsearch icon in the right-click menu. Needs the context menu on.",
    ),
    ConfigKey.SHELL_INTEGRATION_FILE_EXTENSIONS: SettingDescription(
        "File extensions",
        "Which video types show Subsearch when right-clicked. Needs the context menu on.",
    ),
    ConfigKey.NOTIFICATIONS_SYSTEM_TRAY: SettingDescription(
        "Desktop notifications",
        "Show Windows notifications while Subsearch runs and when it finishes.",
    ),
    ConfigKey.NOTIFICATIONS_DISPLAY_DURATION: SettingDescription(
        "Display duration",
        "How long a notification stays on screen, in seconds. Use Test to preview it.",
    ),
    ConfigKey.NOTIFICATIONS_PLAY_SOUND: SettingDescription(
        "Notification sound",
        "Play the Windows chime when a notification appears.",
    ),
    ConfigKey.SUBTITLE_WORKSPACE_SEARCH_MODE: SettingDescription(
        "Search mode",
        "Manual opens the workspace and lets you pick from a list. " "Automatic downloads the best matches on its own.",
    ),
    ConfigKey.SUBTITLE_WORKSPACE_UI_VISIBILITY: SettingDescription(
        "Show the workspace",
        "For automatic searches: Always opens the workspace and runs the search there, "
        "On attention required only opens it when nothing matched, and Never stays hidden.",
    ),
    ConfigKey.PATHS_DOWNLOAD_DIRECTORY: SettingDescription(
        "Download subtitles to",
        "Where downloads are saved before they're unzipped. " "Leave empty to use a temp folder that cleans itself up.",
    ),
    ConfigKey.PATHS_EXTRACTION_DIRECTORY: SettingDescription(
        "Extract subtitles to",
        "Where subtitles are unzipped when there's no video file. " "Leave empty to use your Downloads folder.",
    ),
    ConfigKey.PATHS_VIDEO_FILE_DIRECTORY: SettingDescription(
        "Rename and move subtitles to",
        "Where the best match is renamed and moved, next to the video or a fixed folder. "
        "Ignored when there's no video file.",
    ),
    ConfigKey.PATHS_PATH_RESOLUTION: SettingDescription(
        "Path resolution",
        "Whether the folder above is next to the video or a fixed folder on your drive.",
    ),
    ConfigKey.PATHS_CREATE_MISSING_DIRECTORY: SettingDescription(
        "Create missing directory",
        "Create the folder above if it doesn't exist yet.",
    ),
    CardKey.AVAILABLE_SUBTITLES: SettingDescription(
        "Subtitle workspace",
        "Every subtitle found for this video, best matches first. Double click one to download it. "
        "With automatic downloads on, the best ones are already ticked and placed for you.",
    ),
    ConfigKey.POST_PROCESSING_RENEAME: SettingDescription(
        "Rename subtitle",
        "Rename the subtitle to match your video so players find it on their own.",
    ),
    ConfigKey.POST_PROCESSING_MOVE_BEST: SettingDescription(
        "Move best subtitle",
        "Move only the best subtitle to your chosen folder. Can't be used with Move all.",
    ),
    ConfigKey.POST_PROCESSING_MOVE_ALL: SettingDescription(
        "Move all subtitles",
        "Move every downloaded subtitle to your chosen folder. Can't be used with Move best.",
    ),
    ConfigKey.APPLICATION_MICA_EFFECT: SettingDescription(
        "Mica background effect",
        "Opaque backdrop for windows.",
    ),
    ConfigKey.APPLICATION_SHOW_TERMINAL: SettingDescription(
        "Show terminal while searching",
        "Keep the console window open during a search.",
    ),
    ConfigKey.APPLICATION_SHOW_TRAY_ICON: SettingDescription(
        "Show system tray icon",
        "Show the Subsearch icon in the system tray while the window is open.",
    ),
    ConfigKey.APPLICATION_SINGLE_INSTANCE: SettingDescription(
        "Single instance",
        "Allow only one copy of Subsearch to run at a time.",
    ),
    ConfigKey.SEARCH_DOWNLOADS_PER_PROVIDER: SettingDescription(
        "Downloads per provider",
        "How many subtitles to download from each provider. " "Too high may get your connection blocked for a while.",
    ),
    ConfigKey.NETWORK_REQUEST_CONNECT_TIMEOUT: SettingDescription(
        "Connect timeout",
        "Seconds to wait for a site to respond before giving up.",
    ),
    ConfigKey.NETWORK_REQUEST_READ_TIMEOUT: SettingDescription(
        "Read timeout",
        "Seconds to wait for a site to reply before giving up.",
    ),
    CardKey.DIAGNOSTICS_HEADER: SettingDescription(
        "Provider diagnostics",
        "Health checks run on your computer; nothing is sent anywhere. Reporting issues is up to you.",
    ),
    ConfigKey.DIAGNOSTICS_ENABLED: SettingDescription(
        "Provider diagnostics checks",
        "After a provider fails several searches in a row, run a health check and tell you the result.",
    ),
    ConfigKey.DIAGNOSTICS_FAILED_ATTEMPTS_THRESHOLD: SettingDescription(
        "Failed attempts before check",
        "How many empty searches in a row trigger a check. Resets once the provider finds something.",
    ),
    CardKey.SUBSOURCE_API_KEY: SettingDescription(
        "Subsource API key",
        "Your Subsource API key, stored only on this computer. Without it, Subsource is skipped.",
    ),
    CardKey.SUBSOURCE_REQUEST_LIMITS: SettingDescription(
        "Request limits",
        "Each API key allows 60 requests per minute, 1800 per hour, and 7200 per day.",
    ),
    CardKey.SUBSOURCE_GETTING_API_KEY: SettingDescription(
        "Getting an API key",
        'Open "My Profile" on Subsource and generate a key. Keep it secret.',
    ),
    CardKey.SUBTITLE_FILTERS: SettingDescription(
        "Subtitle filters",
        "Which subtitle types to get. Turn on both to accept hearing-impaired and normal ones.",
    ),
    CardKey.SUBTITLE_HANDLING: SettingDescription(
        "Automatic subtitle handling",
        "What to do with a subtitle after it's downloaded automatically.",
    ),
    CardKey.PATHS: SettingDescription(
        "Paths",
        "Where Subsearch downloads, extracts, and places subtitles.",
    ),
    CardKey.SHELL_INTEGRATION: SettingDescription(
        "Shell integration",
        "Adds Subsearch to the Windows right-click menu for video files.",
    ),
    CardKey.NOTIFICATIONS: SettingDescription(
        "Notifications",
        "Windows notifications shown while Subsearch runs and when a search finishes.",
    ),
    CardKey.APPLICATION: SettingDescription(
        "Application",
        "General behaviour, like showing the terminal during a search and running only one copy at a time.",
    ),
    CardKey.NETWORK: SettingDescription(
        "Network",
        "How many subtitles to get per provider and how long to wait for a site before giving up.",
    ),
    CardKey.UPDATE: SettingDescription(
        "Update",
        "Check for a newer version and install it. The installer runs on its own once downloaded.",
    ),
    CardKey.RESOURCES: SettingDescription(
        "Resources",
        "Report bugs, share crash logs, view third-party licenses and more.",
    ),
}
