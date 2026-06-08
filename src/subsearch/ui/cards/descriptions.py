from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SettingDescription:
    title: str
    explanation: str


SETTING_DESCRIPTIONS: dict[str, SettingDescription] = {
    "language.selected": SettingDescription(
        "Subtitle language",
        "The language you want subtitles in.\n\n"
        "Start typing to narrow the list, e.g. ml, mal or Malayalam all find Malayalam.\n"
        "Press Enter to pick the highlighted language.",
    ),
    "search.accept_threshold": SettingDescription(
        "Filename match threshold",
        "How closely a subtitle's filename has to match your video before Subsearch accepts it. "
        "Higher means stricter matching; lower lets through looser ones.",
    ),
    "search.hearing_impaired": SettingDescription(
        "Hearing impaired",
        "Include subtitles that also describe sounds and note who is speaking, "
        "in addition to the dialogue.",
    ),
    "search.non_hearing_impaired": SettingDescription(
        "Non-hearing impaired",
        "Include standard subtitles that show only the spoken words.",
    ),
    "search.only_foreign_parts": SettingDescription(
        "Foreign parts only",
        "Only look for subtitles that translate the foreign-language sections of a video, "
        "not the whole thing.",
    ),
    "search.providers": SettingDescription(
        "Subtitle providers",
        "The subtitle sites Subsearch looks through. Turn one off to skip it.\n\n"
        "A greyed-out provider doesn't offer subtitles in {language}.",
    ),
    "shell_integration.context_menu": SettingDescription(
        "Context menu",
        "Add Subsearch to the right-click menu for video files in File Explorer.",
    ),
    "shell_integration.context_menu_icon": SettingDescription(
        "Context menu icon",
        "Show the Subsearch icon in the right-click menu. Needs the context menu turned on.",
    ),
    "shell_integration.file_extensions": SettingDescription(
        "File extensions",
        "Which video file types show the Subsearch entry when right-clicked. "
        "Needs the context menu turned on.",
    ),
    "notifications.system_tray": SettingDescription(
        "System tray icon",
        "Show a Subsearch icon next to the clock while it runs. "
        "Status updates and the finished notification appear there.",
    ),
    "notifications.summary_notification": SettingDescription(
        "Summary notification",
        "Pop up a notification when a search finishes. Needs the system tray icon turned on.",
    ),
    "download.automatic": SettingDescription(
        "Automatic downloads",
        "Automatically download the best matching subtitle instead of showing every match for you to pick from.",
    ),
    "download.always_open_manager": SettingDescription(
        "Always open download manager",
        "Open the download manager after every search so you can choose a subtitle yourself. "
        "Can't be used together with opening it only when nothing matches.",
    ),
    "download.open_manager_on_no_matches": SettingDescription(
        "Open manager on no matches",
        "Open the download manager only when nothing matched automatically. "
        "Can't be used together with always opening it.",
    ),
    "download_manager.available_subtitles": SettingDescription(
        "Available subtitles",
        "Every subtitle found for this video, closest matches at the top. Click one to download it. "
        "If automatic downloads are on, the best ones are already downloaded and ticked.",
    ),
    "post_processing.rename": SettingDescription(
        "Rename subtitle",
        "Rename the subtitle to match your video's filename. Most media players need this to find it automatically.",
    ),
    "post_processing.move_best": SettingDescription(
        "Move best subtitle",
        "Move only the single best subtitle to the folder you choose. "
        "Can't be used together with moving all of them.",
    ),
    "post_processing.move_all": SettingDescription(
        "Move all subtitles",
        "Move every downloaded subtitle to the folder you choose. "
        "Can't be used together with moving only the best one.",
    ),
    "post_processing.target_path": SettingDescription(
        "Destination folder",
        "The folder subtitles are moved to. Can be relative to the video's folder or a fixed path on your drive.",
    ),
    "post_processing.path_resolution": SettingDescription(
        "Path resolution",
        "Whether the destination folder is relative to the video's folder or a fixed path on your drive.",
    ),
    "post_processing.create_missing_folder": SettingDescription(
        "Create missing folder",
        "Automatically create the destination folder if it doesn't exist yet.",
    ),
    "application.show_terminal": SettingDescription(
        "Show terminal while searching",
        "Keep the console window open during a search. Only works when running from Python, not the installed app.",
    ),
    "application.single_instance": SettingDescription(
        "Single instance",
        "Only allow one instance of Subsearch to run at a time.",
    ),
    "network.api_call_limit": SettingDescription(
        "API call limit",
        "How many subtitles Subsearch downloads from a single site per search. "
        "It keeps the {limit} best matches and skips the rest. "
        "Setting this too high may get your connection temporarily blocked.",
    ),
    "network.request_connect_timeout": SettingDescription(
        "Connect timeout",
        "How many seconds to wait for a site to respond before giving up.",
    ),
    "network.request_read_timeout": SettingDescription(
        "Read timeout",
        "How many seconds to wait for a site to finish sending its reply before giving up.",
    ),
    "diagnostics.header": SettingDescription(
        "Provider diagnostics",
        "Health checks run locally and nothing is sent anywhere automatically. "
        "Reporting issues to the developer is entirely up to you.",
    ),
    "diagnostics.enabled": SettingDescription(
        "Provider diagnostics checks",
        "Run a health check on a provider after it fails several searches in a row, "
        "then notify you with the result.",
    ),
    "diagnostics.failed_attempts_threshold": SettingDescription(
        "Failed attempts before check",
        "How many searches in a row with no results trigger a health check for that provider. "
        "Resets as soon as the provider finds something.",
    ),
    "credentials.subsource_api_key": SettingDescription(
        "Subsource API key",
        "Your Subsource API key. Without it, Subsearch skips Subsource entirely. "
        "Stored only on this computer.",
    ),
    "credentials.subsource_request_limits": SettingDescription(
        "Request limits",
        "Each API key allows 60 requests per minute, 1800 per hour, and 7200 per day.",
    ),
    "credentials.subsource_getting_api_key": SettingDescription(
        "Getting an API key",
        'Go to your Subsource profile, open "My Profile", and generate a key. '
        "Keep it secret.",
    ),
}
