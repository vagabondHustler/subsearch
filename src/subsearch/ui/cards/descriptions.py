from dataclasses import dataclass

from subsearch.runtime.keys import CardKey, ConfigKey


@dataclass(frozen=True, slots=True)
class SettingDescription:
    title: str
    explanation: str


SETTING_DESCRIPTIONS: dict[ConfigKey | CardKey, SettingDescription] = {
    ConfigKey.LANGUAGE_SELECTED: SettingDescription(
        "Subtitle language",
        "The language you want subtitles in.\n\n"
        "Start typing to narrow the list, e.g. ml, mal or Malayalam all find Malayalam.\n"
        "Press Enter to pick the highlighted language.",
    ),
    ConfigKey.SEARCH_ACCEPT_THRESHOLD: SettingDescription(
        "Filename match threshold",
        "How closely a subtitle's filename has to match your video before Subsearch accepts it. "
        "Higher means stricter matching; lower lets through looser ones.\n\n"
        "The examples below show how three sample subtitles score against your video, "
        "and which ones the current threshold accepts.",
    ),
    ConfigKey.SEARCH_TOKEN_WEIGHTS: SettingDescription(
        "Weights",
        "How much each part of the filename counts towards the match score: the title, "
        "the source like BluRay or WEB, and the release group.\n\n"
        "Raise a weight to let that part sway the score more, lower it to make it matter less.",
    ),
    ConfigKey.SEARCH_TOKEN_MULTIPLIERS: SettingDescription(
        "Mismatch multiplier",
        "How hard the score is cut when a part clearly disagrees: a different year, a different "
        "season or episode, or a different edition.\n\n"
        "The score is multiplied by this value, so 1.0 keeps the score untouched and 0.01 "
        "collapses it almost to nothing. Lower rejects the mismatch harder.",
    ),
    ConfigKey.SEARCH_HEARING_IMPAIRED: SettingDescription(
        "Hearing impaired",
        "Include subtitles that also describe sounds and note who is speaking, " "in addition to the dialogue.",
    ),
    ConfigKey.SEARCH_NON_HEARING_IMPAIRED: SettingDescription(
        "Non-hearing impaired",
        "Include standard subtitles that show only the spoken words.",
    ),
    ConfigKey.SEARCH_ONLY_FOREIGN_PARTS: SettingDescription(
        "Foreign parts only",
        "Only look for subtitles that translate the foreign-language sections of a video, " "not the whole thing.",
    ),
    ConfigKey.SEARCH_PROVIDERS: SettingDescription(
        "Subtitle providers",
        "The subtitle sites Subsearch looks through. Turn one off to skip it.\n\n"
        "A greyed-out provider doesn't offer subtitles in {language}.",
    ),
    ConfigKey.SHELL_INTEGRATION_CONTEXT_MENU: SettingDescription(
        "Context menu",
        "Add Subsearch to the right-click menu for video files in File Explorer.",
    ),
    ConfigKey.SHELL_INTEGRATION_CONTEXT_MENU_ICON: SettingDescription(
        "Context menu icon",
        "Show the Subsearch icon in the right-click menu. Needs the context menu turned on.",
    ),
    ConfigKey.SHELL_INTEGRATION_FILE_EXTENSIONS: SettingDescription(
        "File extensions",
        "Which video file types show the Subsearch entry when right-clicked. " "Needs the context menu turned on.",
    ),
    ConfigKey.NOTIFICATIONS_SYSTEM_TRAY: SettingDescription(
        "System tray icon",
        "Show a Subsearch icon next to the clock while it runs. "
        "Status updates and the finished notification appear there.",
    ),
    ConfigKey.NOTIFICATIONS_SUMMARY_NOTIFICATION: SettingDescription(
        "Summary notification",
        "Pop up a notification when a search finishes. Needs the system tray icon turned on.",
    ),
    ConfigKey.SUBTITLE_WORKSPACE_SEARCH_MODE: SettingDescription(
        "Search mode",
        "Manual: always open the download manager so you pick the subtitle yourself. "
        "Hybrid: auto-download the best match; open the manager only when nothing qualifies. "
        "Automatic: always auto-download silently, never open the manager.",
    ),
    ConfigKey.SUBTITLE_WORKSPACE_MANUAL_POST_PROCESSING: SettingDescription(
        "Disable automatic post-processing",
        "You pick and process subtitles yourself from the search results. "
        "The automatic rename and move options above are disabled while this is active.",
    ),
    ConfigKey.PATHS_DOWNLOAD_DIRECTORY: SettingDescription(
        "Download subtitles to",
        "Where subtitle archives are downloaded to before they are extracted. "
        "Leave empty to use the system temporary directory, which is cleaned up automatically.",
    ),
    ConfigKey.PATHS_EXTRACTION_DIRECTORY: SettingDescription(
        "Exctract subtitles to",
        "Where downloaded archives are extracted to when searching without a video file. "
        "Leave empty to use your Downloads directory.",
    ),
    ConfigKey.PATHS_VIDEO_FILE_DIRECTORY: SettingDescription(
        "Rename and move subtitles to",
        "The directory the best match is renamed and moved to. Can be relative to the video's "
        "directory or a fixed path on your drive. Ignored when no video file backs the search.",
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
        "Subtitles",
        "Every subtitle found for this video, closest matches at the top. Click one to download it. "
        "If automatic downloads are on, the best ones are already downloaded and ticked.",
    ),
    ConfigKey.POST_PROCESSING_RENEAME: SettingDescription(
        "Rename subtitle",
        "Rename the subtitle to match your video's filename. Most media players need this to find it automatically.",
    ),
    ConfigKey.POST_PROCESSING_MOVE_BEST: SettingDescription(
        "Move best subtitle",
        "Move only the single best subtitle to the directory you choose. "
        "Can't be used together with moving all of them.",
    ),
    ConfigKey.POST_PROCESSING_MOVE_ALL: SettingDescription(
        "Move all subtitles",
        "Move every downloaded subtitle to the folder you choose. "
        "Can't be used together with moving only the best one.",
    ),
    ConfigKey.APPLICATION_SHOW_TERMINAL: SettingDescription(
        "Show terminal while searching",
        "Keep the console window open during a search. Only works when running from Python, not the installed app.",
    ),
    ConfigKey.APPLICATION_SINGLE_INSTANCE: SettingDescription(
        "Single instance",
        "Only allow one instance of Subsearch to run at a time.",
    ),
    ConfigKey.SEARCH_DOWNLOADS_PER_PROVIDER: SettingDescription(
        "Downloads per provider",
        "How many subtitles Subsearch downloads from a single provider per search. "
        "It keeps the {limit} best matches and skips the rest. "
        "Setting this too high may get your connection temporarily blocked.",
    ),
    ConfigKey.NETWORK_REQUEST_CONNECT_TIMEOUT: SettingDescription(
        "Connect timeout",
        "How many seconds to wait for a site to respond before giving up.",
    ),
    ConfigKey.NETWORK_REQUEST_READ_TIMEOUT: SettingDescription(
        "Read timeout",
        "How many seconds to wait for a site to finish sending its reply before giving up.",
    ),
    CardKey.DIAGNOSTICS_HEADER: SettingDescription(
        "Provider diagnostics",
        "Health checks run locally and nothing is sent anywhere automatically. "
        "Reporting issues to the developer is entirely up to you.",
    ),
    ConfigKey.DIAGNOSTICS_ENABLED: SettingDescription(
        "Provider diagnostics checks",
        "Run a health check on a provider after it fails several searches in a row, "
        "then notify you with the result.",
    ),
    ConfigKey.DIAGNOSTICS_FAILED_ATTEMPTS_THRESHOLD: SettingDescription(
        "Failed attempts before check",
        "How many searches in a row with no results trigger a health check for that provider. "
        "Resets as soon as the provider finds something.",
    ),
    CardKey.SUBSOURCE_API_KEY: SettingDescription(
        "Subsource API key",
        "Your Subsource API key. Without it, Subsearch skips Subsource entirely. " "Stored only on this computer.",
    ),
    CardKey.SUBSOURCE_REQUEST_LIMITS: SettingDescription(
        "Request limits",
        "Each API key allows 60 requests per minute, 1800 per hour, and 7200 per day.",
    ),
    CardKey.SUBSOURCE_GETTING_API_KEY: SettingDescription(
        "Getting an API key",
        'Go to your Subsource profile, open "My Profile", and generate a key. ' "Keep it secret.",
    ),
    CardKey.SUBTITLE_FILTERS: SettingDescription(
        "Subtitle filters",
        "Control which subtitle types Subsearch fetches. "
        "You can combine hearing-impaired and non-hearing-impaired to accept both, "
        "or enable foreign-parts-only to target films with untranslated sections.",
    ),
    CardKey.SUBTITLE_HANDLING: SettingDescription(
        "Subtitle handling",
        "What Subsearch does with a subtitle after finding it. "
        "Automatically rename and move it to the video file directory, "
        "or take over and process subtitles yourself from the search results.",
    ),
    CardKey.PATHS: SettingDescription(
        "Paths",
        "Where Subsearch downloads, extracts, and places subtitles. " "Leave a folder empty to use its default.",
    ),
    CardKey.SHELL_INTEGRATION: SettingDescription(
        "Shell integration",
        "Adds Subsearch to the Windows right-click context menu for video files. "
        "Requires administrator privileges to write to the registry.",
    ),
    CardKey.NOTIFICATIONS: SettingDescription(
        "Notifications",
        "Controls the system tray icon and the pop-up that appears when a search finishes. "
        "The summary notification requires the tray icon to be turned on.",
    ),
    CardKey.APPLICATION: SettingDescription(
        "Application",
        "General application behaviour. "
        "Show the terminal window during a search (Python only), "
        "and prevent more than one instance of Subsearch from running at once.",
    ),
    CardKey.NETWORK: SettingDescription(
        "Network",
        "Caps how many subtitle files are fetched from each provider per search, "
        "and sets how long Subsearch waits for a site to respond before giving up.",
    ),
    CardKey.UPDATE: SettingDescription(
        "Update",
        "Check whether a newer version of Subsearch is available and install it. "
        "The installer runs automatically after the download finishes.",
    ),
    CardKey.RESOURCES: SettingDescription(
        "Resources",
        "Shortcuts for reporting bugs, sharing crash logs with the developer, "
        "viewing third-party licenses, and browsing the source code on GitHub.",
    ),
}
