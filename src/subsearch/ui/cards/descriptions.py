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
        "How closely a subtitle's filename must match your video to be accepted. "
        "Higher is stricter; lower lets looser matches through.",
    ),
    ConfigKey.SEARCH_TOKEN_WEIGHTS: SettingDescription(
        "Weights",
        "How much the title, source (BluRay, WEB), and release group each count towards the match score. "
        "Raise one to give it more say.",
    ),
    ConfigKey.SEARCH_TOKEN_MULTIPLIERS: SettingDescription(
        "Mismatch multiplier",
        "How hard to cut the score when a part clearly disagrees (year, season, episode, edition). "
        "1.0 keeps it as is; lower rejects mismatches harder.",
    ),
    ConfigKey.SEARCH_HEARING_IMPAIRED: SettingDescription(
        "Hearing impaired",
        "Include subtitles that also describe sounds and note who is speaking.",
    ),
    ConfigKey.SEARCH_NON_HEARING_IMPAIRED: SettingDescription(
        "Non-hearing impaired",
        "Include standard subtitles that show only the spoken words.",
    ),
    ConfigKey.SEARCH_ONLY_FOREIGN_PARTS: SettingDescription(
        "Foreign parts only",
        "Only fetch subtitles for the foreign-language sections of a video, not the whole thing.",
    ),
    ConfigKey.SEARCH_PROVIDERS: SettingDescription(
        "Subtitle providers",
        "The subtitle sites Subsearch searches. Turn one off to skip it. "
        "Greyed-out providers have no subtitles in {language}.",
    ),
    ConfigKey.SHELL_INTEGRATION_CONTEXT_MENU: SettingDescription(
        "Context menu",
        "Add Subsearch to the right-click menu for video files in File Explorer.",
    ),
    ConfigKey.SHELL_INTEGRATION_CONTEXT_MENU_ICON: SettingDescription(
        "Context menu icon",
        "Show the Subsearch icon in the right-click menu. Requires the context menu.",
    ),
    ConfigKey.SHELL_INTEGRATION_FILE_EXTENSIONS: SettingDescription(
        "File extensions",
        "Which video file types show the Subsearch entry when right-clicked. Requires the context menu.",
    ),
    ConfigKey.NOTIFICATIONS_SYSTEM_TRAY: SettingDescription(
        "Desktop notifications",
        "Show Windows notifications with status updates and the finished notification while Subsearch runs.",
    ),
    ConfigKey.NOTIFICATIONS_DISPLAY_DURATION: SettingDescription(
        "Display duration",
        "How long, in seconds, a notification stays on screen before it fades out. "
        "Use Test to preview the current duration.",
    ),
    ConfigKey.NOTIFICATIONS_PLAY_SOUND: SettingDescription(
        "Notification sound",
        "Play the Windows notification chime when a notification appears.",
    ),
    ConfigKey.SUBTITLE_WORKSPACE_SEARCH_MODE: SettingDescription(
        "Search mode",
        "Manual opens the download manager so you choose. Hybrid auto-downloads the best match and only "
        "opens the manager when nothing qualifies. Automatic downloads silently.",
    ),
    ConfigKey.PATHS_DOWNLOAD_DIRECTORY: SettingDescription(
        "Download subtitles to",
        "Where archives are downloaded before extraction. "
        "Leave empty for the system temp directory, which is cleaned up automatically.",
    ),
    ConfigKey.PATHS_EXTRACTION_DIRECTORY: SettingDescription(
        "Extract subtitles to",
        "Where archives are extracted when searching without a video file. "
        "Leave empty to use your Downloads directory.",
    ),
    ConfigKey.PATHS_VIDEO_FILE_DIRECTORY: SettingDescription(
        "Rename and move subtitles to",
        "Where the best match is renamed and moved to, relative to the video or a fixed path. "
        "Ignored when no video file backs the search.",
    ),
    ConfigKey.PATHS_PATH_RESOLUTION: SettingDescription(
        "Path resolution",
        "Whether the video file directory is relative to the video's directory or a fixed path on your drive.",
    ),
    ConfigKey.PATHS_CREATE_MISSING_DIRECTORY: SettingDescription(
        "Create missing directory",
        "Automatically create the video file directory if it doesn't exist yet.",
    ),
    CardKey.AVAILABLE_SUBTITLES: SettingDescription(
        "Subtitle workspace",
        "Every subtitle found for this video, closest matches first. Double click one to download it. "
        "With automatic downloads on, the best ones are already ticked. "
        "Downloaded subtitles are extracted and placed automatically.",
    ),
    ConfigKey.POST_PROCESSING_RENEAME: SettingDescription(
        "Rename subtitle",
        "Rename the subtitle to match your video so media players find it automatically.",
    ),
    ConfigKey.POST_PROCESSING_MOVE_BEST: SettingDescription(
        "Move best subtitle",
        "Move only the single best subtitle to your chosen directory. Can't combine with moving all.",
    ),
    ConfigKey.POST_PROCESSING_MOVE_ALL: SettingDescription(
        "Move all subtitles",
        "Move every downloaded subtitle to your chosen directory. Can't combine with moving the best one.",
    ),
    ConfigKey.APPLICATION_MICA_EFFECT: SettingDescription(
        "Mica background effect",
        "Blend the window background with the desktop using the Windows Mica material.",
    ),
    ConfigKey.APPLICATION_SHOW_TERMINAL: SettingDescription(
        "Show terminal while searching",
        "Keep the console window open during a search. Only when running from Python, not the installed app.",
    ),
    ConfigKey.APPLICATION_SHOW_TRAY_ICON: SettingDescription(
        "Show system tray icon",
        "Show the Subsearch icon in the Windows system tray while the window is open.",
    ),
    ConfigKey.APPLICATION_SINGLE_INSTANCE: SettingDescription(
        "Single instance",
        "Only allow one instance of Subsearch to run at a time.",
    ),
    ConfigKey.SEARCH_DOWNLOADS_PER_PROVIDER: SettingDescription(
        "Downloads per provider",
        "How many subtitles to download from each provider per search, keeping the {limit} best. "
        "Too high may get your connection temporarily blocked.",
    ),
    ConfigKey.NETWORK_REQUEST_CONNECT_TIMEOUT: SettingDescription(
        "Connect timeout",
        "Seconds to wait for a site to respond before giving up.",
    ),
    ConfigKey.NETWORK_REQUEST_READ_TIMEOUT: SettingDescription(
        "Read timeout",
        "Seconds to wait for a site to finish replying before giving up.",
    ),
    CardKey.DIAGNOSTICS_HEADER: SettingDescription(
        "Provider diagnostics",
        "Health checks run locally; nothing is sent anywhere automatically. Reporting issues is up to you.",
    ),
    ConfigKey.DIAGNOSTICS_ENABLED: SettingDescription(
        "Provider diagnostics checks",
        "Run a health check after a provider fails several searches in a row, then notify you with the result.",
    ),
    ConfigKey.DIAGNOSTICS_FAILED_ATTEMPTS_THRESHOLD: SettingDescription(
        "Failed attempts before check",
        "How many searches in a row with no results trigger a check. Resets once the provider finds something.",
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
        "Which subtitle types to fetch. Combine hearing-impaired and non-hearing-impaired to accept both.",
    ),
    CardKey.SUBTITLE_HANDLING: SettingDescription(
        "Automatic subtitle handling",
        "What to do with a subtitle after automatically downloading it.",
    ),
    CardKey.PATHS: SettingDescription(
        "Paths",
        "Where Subsearch downloads, extracts, and places subtitles. Leave a folder empty for its default.",
    ),
    CardKey.SHELL_INTEGRATION: SettingDescription(
        "Shell integration",
        "Adds Subsearch to the Windows right-click menu for video files. Requires administrator privileges.",
    ),
    CardKey.NOTIFICATIONS: SettingDescription(
        "Notifications",
        "Windows notifications shown while Subsearch runs and when a search finishes.",
    ),
    CardKey.APPLICATION: SettingDescription(
        "Application",
        "General behaviour: show the terminal during a search (Python only) and limit Subsearch to one instance.",
    ),
    CardKey.NETWORK: SettingDescription(
        "Network",
        "How many subtitles to fetch per provider and how long to wait for a site before giving up.",
    ),
    CardKey.UPDATE: SettingDescription(
        "Update",
        "Check for a newer version and install it. The installer runs automatically once downloaded.",
    ),
    CardKey.RESOURCES: SettingDescription(
        "Resources",
        "Report bugs, share crash logs, view third-party licenses, and browse the source on GitHub.",
    ),
}
