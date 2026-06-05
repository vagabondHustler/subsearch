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
        "How well a subtitle's name has to match your video before Subsearch counts it as a "
        "match. Higher means only very close matches are kept; lower lets through looser ones "
        "that might belong to a different version of the video.",
    ),
    "search.hearing_impaired": SettingDescription(
        "Hearing impaired",
        "Include subtitles made for the hard of hearing. As well as the dialogue, these "
        "describe sounds and note who is speaking.",
    ),
    "search.non_hearing_impaired": SettingDescription(
        "Non-hearing impaired",
        "Include normal subtitles that show only the spoken words, without the extra notes for the hard of hearing.",
    ),
    "search.only_foreign_parts": SettingDescription(
        "Foreign parts only",
        "Only look for subtitles that translate the foreign-language bits of a video, rather "
        "than subtitle the whole thing.",
    ),
    "search.providers": SettingDescription(
        "Subtitle providers",
        "The subtitle sites Subsearch looks through. Turn one off and Subsearch will skip it "
        "when searching.\n\n"
        "A greyed-out provider doesn't offer subtitles in {language}.",
    ),
    "shell_integration.context_menu": SettingDescription(
        "Context menu",
        "Add Subsearch to the menu you get when you right-click a video file, so you can start "
        "a search straight from File Explorer.",
    ),
    "shell_integration.context_menu_icon": SettingDescription(
        "Context menu icon",
        "Show the Subsearch icon next to its entry in the right-click menu. Needs the context menu turned on.",
    ),
    "shell_integration.file_extensions": SettingDescription(
        "File extensions",
        "Choose which kinds of video file show the Subsearch entry when you right-click them. "
        "Only the ticked ones get it. Needs the context menu turned on.",
    ),
    "notifications.system_tray": SettingDescription(
        "System tray icon",
        "Show a Subsearch icon in the system tray (next to the clock) while it runs. This is "
        "where its status and the finished notification appear.",
    ),
    "notifications.summary_notification": SettingDescription(
        "Summary notification",
        "Pop up a notification telling you how a search went once it finishes. Needs the system "
        "tray icon turned on.",
    ),
    "download.automatic": SettingDescription(
        "Automatic downloads",
        "Download the best matching subtitle for you automatically, instead of leaving every "
        "match for you to pick from in the download manager.",
    ),
    "download.always_open_manager": SettingDescription(
        "Always open download manager",
        "Open the download manager after every search so you can pick a subtitle yourself. "
        "Can't be used together with opening it only when nothing matches.",
    ),
    "download.open_manager_on_no_matches": SettingDescription(
        "Open manager on no matches",
        "Open the download manager only when nothing matched automatically, so you can see what "
        "was available and choose. Can't be used together with always opening it.",
    ),
    "download_manager.available_subtitles": SettingDescription(
        "Available subtitles",
        "Every subtitle found for this video, with the closest matches at the top. Click one to "
        "download it: the icon spins while it downloads, then turns into a green tick if it "
        "worked or a red cross if it didn't. If automatic downloads are enabled, some subtitles  "
        "will allready be downloaded and ticked for you.",
    ),
    "post_processing.rename": SettingDescription(
        "Rename subtitle",
        "Rename the subtitle so it matches your video's filename. Most media players need this "
        "to find the subtitle on their own.",
    ),
    "post_processing.move_best": SettingDescription(
        "Move best subtitle",
        "Move just the single best subtitle to the folder you choose. Can't be used together "
        "with moving all of them.",
    ),
    "post_processing.move_all": SettingDescription(
        "Move all subtitles",
        "Move every subtitle you downloaded to the folder you choose. Can't be used together "
        "with moving only the best one.",
    ),
    "post_processing.target_path": SettingDescription(
        "Destination folder",
        "The folder moved subtitles are put in. A relative folder is found starting from the "
        "video's own folder; an absolute one is a fixed location on your drive.",
    ),
    "post_processing.path_resolution": SettingDescription(
        "Path resolution",
        "Whether the destination folder is found starting from the video's folder (relative) or "
        "is a fixed location on your drive (absolute).",
    ),
    "post_processing.create_missing_folder": SettingDescription(
        "Create missing folder",
        "Create the destination folder automatically if it doesn't exist yet, instead of asking first.",
    ),
    "application.show_terminal": SettingDescription(
        "Show terminal while searching",
        "Keep the black console window open during a search so you can watch what Subsearch is "
        "doing. Only works when running from Python, not the installed app.",
    ),
    "application.single_instance": SettingDescription(
        "Single instance",
        "Only let one instance of Subsearch run at a time.",
    ),
    "network.api_call_limit": SettingDescription(
        "API call limit",
        "The most subtitles Subsearch will download from a single site in one search. With a "
        "limit of {limit}, it keeps the {limit} best matches from each site and skips the rest. "
        "Turning this up can get you rate-limited or have your connection temporarily blocked.",
    ),
    "network.request_connect_timeout": SettingDescription(
        "Connect timeout",
        "How many seconds to wait for a site to answer before giving up on reaching it.",
    ),
    "network.request_read_timeout": SettingDescription(
        "Read timeout",
        "Once connected, how many seconds to wait for a site to send its reply before giving up.",
    ),
    "diagnostics.header": SettingDescription(
        "Provider health",
        "Health checks run locally and nothing is sent anywhere automatically. "
        "If a provider looks broken, reporting it to the developer is entirely up to you.",
    ),
    "diagnostics.enabled": SettingDescription(
        "Provider health checks",
        "Runs a test search after the failed-attempts threshold is reached to confirm "
        "whether the provider is actually broken. Notifies you with the result. "
        "Disable to skip checks entirely.",
    ),
    "diagnostics.failed_attempts_threshold": SettingDescription(
        "Failed attempts before check",
        "How many consecutive searches without a result trigger a health check for "
        "that provider. Providers that keep returning results are never checked. "
        "The counter resets to zero as soon as the provider returns a result again.",
    ),
    "credentials.subsource_api_key": SettingDescription(
        "Subsource API key",
        "Your personal Subsource API key. Subsource needs this key to search and "
        "download; without it Subsearch skips Subsource. Create a free account at "
        "subsource.net and copy your key from the API section. The key is stored "
        "only on this computer and is never shared.",
    ),
    "credentials.subsource_request_limits": SettingDescription(
        "Request limits",
        "Each API key is limited to a request limit of 60 per min, 1800 per hour and 7200 per day.",
    ),
    "credentials.subsource_getting_api_key": SettingDescription(
        "Getting an API Key",
        'Create a key from your SubSource profile: open your dashboard, go to "My Profile", '
        "and generate one. You can regenerate it any time. Keep it secret.",
    ),
}
