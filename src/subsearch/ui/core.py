import json
from typing import Any, Callable, Dict, List, Set

import flet as ft

from subsearch.ui.keys import (
    CardKey,
    CardMetaData,
    FieldKey,
    FieldMeta,
    LayoutKind,
    LayoutSpec,
    ScreenKey,
    WidgetType,
)
from subsearch.ui.languages import languages


class Theme:
    def __init__(self) -> None:
        self.height = 40
        self.icon_size = 16
        self.icon_size_big = 64
        self.border_radius = 4
        self.padding = 6
        self.gap = 6
        self.gap_small = 4
        self.icon_size_small = 14
        self.button_square = 24
        self.sidebar_width = 220
        self.card_max_width = 720
        self.input_width = 320
        self.font_size_menu = 14
        self.font_size_text = 12
        self.font_size_subtitle = 11
        self.background = "#1a1b1b"
        self.background_elevated = "#111111"
        self.card_background = "#1a1b1b"
        self.border_color = "#242525"
        self.text_color = "#bdbdbd"
        self.text_muted = "#5a5b5b"
        self.accent_color = "#7a7f49"
        self.accent_hover = "#151515"
        self.danger_color = "#C45C5C"
        self.good = "#7a7f49"
        self.bad = "#C45C5C"

    def style(self, page: ft.Page) -> None:
        page.theme_mode = ft.ThemeMode.DARK
        page.bgcolor = self.background
        page.padding = 0
        page.spacing = 0
        page.theme = ft.Theme(color_scheme_seed=self.accent_color, use_material3=False)
        page.update()


class State:
    def __init__(self, registry: "Registry") -> None:
        self.values: Dict[FieldKey, Any] = {k: m.default for k, m in registry.fields.items()}

    def get(self, key: FieldKey) -> Any:
        return self.values[key]

    def set(self, key: FieldKey, value: Any) -> None:
        self.values[key] = value

    def snapshot(self) -> Dict[str, Any]:
        return {k.name: v for k, v in self.values.items()}

    def load(self, data: Dict[str, Any]) -> None:
        for fk in list(self.values.keys()):
            if fk.name in data:
                self.values[fk] = data[fk.name]


class Dirty:
    def __init__(self) -> None:
        self.changed: Set[FieldKey] = set()
        self.original_values: Dict[FieldKey, Any] = {}

    def set_original_values(self, state: State) -> None:
        self.original_values = {k: v for k, v in state.values.items()}

    def mark(self, key: FieldKey, current_value: Any) -> None:
        if key not in self.original_values:
            self.original_values[key] = current_value
            return

        original_value = self.original_values[key]

        if current_value != original_value:
            self.changed.add(key)
        else:
            self.changed.discard(key)

    def update_originals_after_save(self, state: State) -> None:
        for key in list(self.changed):
            self.original_values[key] = state.values[key]
        self.changed.clear()

    def has_changes(self) -> bool:
        return len(self.changed) > 0


class Registry:
    def __init__(self) -> None:
        self.fields: Dict[FieldKey, FieldMeta] = {}
        self.cards: Dict[CardKey, CardMetaData] = {}
        self.screens: Dict[ScreenKey, Dict[str, Any]] = {}
        self._init_registry()

    def _init_registry(self) -> None:
        self._init_fields()
        self._init_extension_fields()
        self._init_cards()
        self._init_screens()

    def _init_fields(self) -> None:
        self.fields = {
            FieldKey.API_CALL_LIMIT: FieldMeta(
                FieldKey.API_CALL_LIMIT,
                "API Call Limit",
                "Max parallel API calls.",
                WidgetType.INT,
                4,
                [lambda v: isinstance(v, int) and v > 0],
            ),
            FieldKey.REQ_CONNECT_TIMEOUT: FieldMeta(
                FieldKey.REQ_CONNECT_TIMEOUT,
                "Connect Timeout",
                "Seconds to establish connection.",
                WidgetType.INT,
                4,
                [lambda v: isinstance(v, int) and v > 0],
            ),
            FieldKey.REQ_READ_TIMEOUT: FieldMeta(
                FieldKey.REQ_READ_TIMEOUT,
                "Read Timeout",
                "Seconds to read response.",
                WidgetType.INT,
                5,
                [lambda v: isinstance(v, int) and v > 0],
            ),
            FieldKey.ACCEPT_THRESHOLD: FieldMeta(
                FieldKey.ACCEPT_THRESHOLD,
                "Accept Threshold",
                "Minimum score to accept [0–100].",
                WidgetType.SLIDER,
                50,
                [lambda v: isinstance(v, int) and 0 <= v <= 100],
            ),
            FieldKey.OPEN_ON_NO_MATCHES: FieldMeta(
                FieldKey.OPEN_ON_NO_MATCHES,
                "Open Picker On No Matches",
                "Open file picker when no matches.",
                WidgetType.RADIO_PICKER,
                True,
                [lambda v: isinstance(v, bool)],
            ),
            FieldKey.ALWAYS_OPEN: FieldMeta(
                FieldKey.ALWAYS_OPEN,
                "Always Open Picker",
                "Always open file picker.",
                WidgetType.RADIO_PICKER,
                False,
                [lambda v: isinstance(v, bool)],
            ),
            FieldKey.AUTO_DOWNLOADS: FieldMeta(
                FieldKey.AUTO_DOWNLOADS,
                "Automatic Downloads",
                "Download best match automatically.",
                WidgetType.BOOL,
                True,
                [lambda v: isinstance(v, bool)],
            ),
            FieldKey.CONTEXT_MENU: FieldMeta(
                FieldKey.CONTEXT_MENU,
                "Enable Context Menu",
                "Enable shell context menu.",
                WidgetType.BOOL,
                True,
                [lambda v: isinstance(v, bool)],
            ),
            FieldKey.CONTEXT_MENU_ICON: FieldMeta(
                FieldKey.CONTEXT_MENU_ICON,
                "Show Context Menu Icon",
                "Show icon in context menu.",
                WidgetType.BOOL,
                True,
                [lambda v: isinstance(v, bool)],
            ),
            FieldKey.SYSTEM_TRAY: FieldMeta(
                FieldKey.SYSTEM_TRAY,
                "System Tray",
                "Show app in system tray.",
                WidgetType.BOOL,
                True,
                [lambda v: isinstance(v, bool)],
            ),
            FieldKey.SUMMARY_NOTIFICATION: FieldMeta(
                FieldKey.SUMMARY_NOTIFICATION,
                "Summary Notification",
                "Notify when tasks finish.",
                WidgetType.BOOL,
                False,
                [lambda v: isinstance(v, bool)],
            ),
            FieldKey.SHOW_TERMINAL: FieldMeta(
                FieldKey.SHOW_TERMINAL,
                "Show Terminal",
                "Open terminal on start.",
                WidgetType.BOOL,
                False,
                [lambda v: isinstance(v, bool)],
            ),
            FieldKey.SINGLE_INSTANCE: FieldMeta(
                FieldKey.SINGLE_INSTANCE,
                "Single Instance",
                "Allow only one instance.",
                WidgetType.BOOL,
                True,
                [lambda v: isinstance(v, bool)],
            ),
            FieldKey.OS_SITE: FieldMeta(
                FieldKey.OS_SITE,
                "OpenSubtitles (site)",
                "Enable OpenSubtitles site provider.",
                WidgetType.BOOL,
                True,
                [lambda v: isinstance(v, bool)],
            ),
            FieldKey.OS_HASH: FieldMeta(
                FieldKey.OS_HASH,
                "OpenSubtitles (hash)",
                "Enable OpenSubtitles hash provider.",
                WidgetType.BOOL,
                True,
                [lambda v: isinstance(v, bool)],
            ),
            FieldKey.YIFY_SITE: FieldMeta(
                FieldKey.YIFY_SITE,
                "YIFYSubtitles",
                "Enable YIFYSubtitles provider.",
                WidgetType.BOOL,
                True,
                [lambda v: isinstance(v, bool)],
            ),
            FieldKey.SUBSOURCE_SITE: FieldMeta(
                FieldKey.SUBSOURCE_SITE,
                "Subsource",
                "Enable Subsource provider.",
                WidgetType.BOOL,
                True,
                [lambda v: isinstance(v, bool)],
            ),
            FieldKey.CURRENT_LANGUAGE: FieldMeta(
                FieldKey.CURRENT_LANGUAGE,
                "Preferred Language",
                "Language for subtitle search.",
                WidgetType.LANGUAGE,
                "english",
                [lambda v: v in languages],
            ),
            FieldKey.HEARING_IMPAIRED: FieldMeta(
                FieldKey.HEARING_IMPAIRED,
                "Hearing Impaired",
                "Prefer hearing-impaired subs.",
                WidgetType.BOOL,
                True,
                [lambda v: isinstance(v, bool)],
            ),
            FieldKey.NON_HEARING_IMPAIRED: FieldMeta(
                FieldKey.NON_HEARING_IMPAIRED,
                "Non Hearing Impaired",
                "Prefer non-hearing-impaired subs.",
                WidgetType.BOOL,
                True,
                [lambda v: isinstance(v, bool)],
            ),
            FieldKey.ONLY_FOREIGN_PARTS: FieldMeta(
                FieldKey.ONLY_FOREIGN_PARTS,
                "Only Foreign Parts",
                "Only foreign language parts.",
                WidgetType.BOOL,
                False,
                [lambda v: isinstance(v, bool)],
            ),
            FieldKey.RENAME: FieldMeta(
                FieldKey.RENAME,
                "Rename",
                "Rename downloaded subtitle to match media.",
                WidgetType.BOOL,
                True,
                [lambda v: isinstance(v, bool)],
            ),
            FieldKey.MOVE_BEST: FieldMeta(
                FieldKey.MOVE_BEST,
                "Move Best",
                "Move best subtitle only.",
                WidgetType.RADIO_MOVE,
                True,
                [lambda v: isinstance(v, bool)],
            ),
            FieldKey.MOVE_ALL: FieldMeta(
                FieldKey.MOVE_ALL,
                "Move All",
                "Move all downloaded subtitles.",
                WidgetType.RADIO_MOVE,
                False,
                [lambda v: isinstance(v, bool)],
            ),
            FieldKey.TARGET_PATH: FieldMeta(
                FieldKey.TARGET_PATH,
                "Target Path",
                "Destination for moved subtitles.",
                WidgetType.TEXT,
                ".",
                [lambda v: isinstance(v, str) and len(v.strip()) > 0],
            ),
            FieldKey.PATH_RESOLUTION: FieldMeta(
                FieldKey.PATH_RESOLUTION,
                "Path Resolution",
                "How to resolve target path.",
                WidgetType.SELECT,
                "relative",
                [lambda v: v in {"relative", "absolute"}],
            ),
        }

    def _init_extension_fields(self) -> None:
        extensions = {
            FieldKey.EXT_AVI: "avi",
            FieldKey.EXT_MP4: "mp4",
            FieldKey.EXT_MKV: "mkv",
            FieldKey.EXT_MPG: "mpg",
            FieldKey.EXT_MPEG: "mpeg",
            FieldKey.EXT_MOV: "mov",
            FieldKey.EXT_RM: "rm",
            FieldKey.EXT_VOB: "vob",
            FieldKey.EXT_WMV: "wmv",
            FieldKey.EXT_FLV: "flv",
            FieldKey.EXT_3GP: "3gp",
            FieldKey.EXT_3G2: "3g2",
            FieldKey.EXT_SWF: "swf",
            FieldKey.EXT_MSWMM: "mswmm",
        }
        for fk, ext in extensions.items():
            self.fields[fk] = FieldMeta(
                fk,
                ext.upper(),
                f"Include *.{ext} in context menu.",
                WidgetType.BOOL,
                True,
                [lambda v: isinstance(v, bool)],
            )

    def _init_cards(self) -> None:
        self.cards = {
            CardKey.PROVIDER_NETWORKS: CardMetaData(
                "Provider Networks",
                ft.Icons.LAN,
                [FieldKey.API_CALL_LIMIT, FieldKey.REQ_CONNECT_TIMEOUT, FieldKey.REQ_READ_TIMEOUT],
                spacing_override=4,
            ),
            CardKey.DOWNLOAD: CardMetaData(
                "Download Settings",
                ft.Icons.DOWNLOAD,
                [FieldKey.ACCEPT_THRESHOLD, FieldKey.AUTO_DOWNLOADS, FieldKey.OPEN_ON_NO_MATCHES],
            ),
            CardKey.CONTEXT_MENU: CardMetaData(
                "Context Menu",
                ft.Icons.MENU_OPEN,
                [],
                layout=[
                    LayoutSpec(LayoutKind.STACK, [FieldKey.CONTEXT_MENU, FieldKey.CONTEXT_MENU_ICON]),
                    LayoutSpec(
                        LayoutKind.EXTENSIONS,
                        [],
                        col={"xs": 6, "sm": 4, "md": 3, "lg": 3},
                        title="Applies to file extensions",
                    ),
                ],
            ),
            CardKey.FILE_EXT: CardMetaData("File Extensions", ft.Icons.EXTENSION, []),
            CardKey.APP: CardMetaData(
                "App Settings",
                ft.Icons.APP_SETTINGS_ALT,
                [FieldKey.SYSTEM_TRAY, FieldKey.SUMMARY_NOTIFICATION, FieldKey.SHOW_TERMINAL, FieldKey.SINGLE_INSTANCE],
            ),
            CardKey.PROVIDERS: CardMetaData(
                "Providers",
                ft.Icons.CLOUD_SYNC,
                [],
                layout=[
                    LayoutSpec(
                        LayoutKind.GRID,
                        [FieldKey.OS_SITE, FieldKey.OS_HASH, FieldKey.YIFY_SITE, FieldKey.SUBSOURCE_SITE],
                        col={"xs": 12, "md": 6},
                    )
                ],
            ),
            CardKey.SUBTITLE_STYLE: CardMetaData(
                "Subtitle Style",
                ft.Icons.SUBTITLES,
                [],
                layout=[
                    LayoutSpec(LayoutKind.STACK, [FieldKey.CURRENT_LANGUAGE]),
                    LayoutSpec(
                        LayoutKind.ROW,
                        [FieldKey.HEARING_IMPAIRED, FieldKey.NON_HEARING_IMPAIRED, FieldKey.ONLY_FOREIGN_PARTS],
                    ),
                ],
            ),
            CardKey.HANDLE_DOWNLOADED: CardMetaData(
                "Handle Downloaded Subtitles",
                ft.Icons.DRIVE_FILE_MOVE,
                [FieldKey.RENAME, FieldKey.MOVE_BEST, FieldKey.TARGET_PATH, FieldKey.PATH_RESOLUTION],
            ),
            CardKey.ABOUT: CardMetaData("About", ft.Icons.INFO, []),
        }

    def _init_screens(self) -> None:
        self.screens = {
            ScreenKey.APP: {
                "title": "App Settings",
                "icon": ft.Icons.TUNE,
                "cards": [CardKey.APP, CardKey.CONTEXT_MENU],
            },
            ScreenKey.SEARCH: {
                "title": "Search Settings",
                "icon": ft.Icons.SEARCH,
                "cards": [CardKey.SUBTITLE_STYLE, CardKey.PROVIDERS, CardKey.PROVIDER_NETWORKS],
            },
            ScreenKey.DOWNLOAD: {
                "title": "Download Settings",
                "icon": ft.Icons.DOWNLOAD,
                "cards": [CardKey.DOWNLOAD, CardKey.HANDLE_DOWNLOADED],
            },
            ScreenKey.ABOUT: {"title": "About", "icon": ft.Icons.INFO, "cards": [CardKey.ABOUT]},
        }


class Rules:
    def apply(self, state: State) -> None:
        if not state.get(FieldKey.CONTEXT_MENU):
            state.set(FieldKey.CONTEXT_MENU_ICON, False)
        a = state.get(FieldKey.OPEN_ON_NO_MATCHES)
        b = state.get(FieldKey.ALWAYS_OPEN)
        if a == b:
            state.set(FieldKey.ALWAYS_OPEN, not a)
        mb = state.get(FieldKey.MOVE_BEST)
        ma = state.get(FieldKey.MOVE_ALL)
        if mb == ma:
            state.set(FieldKey.MOVE_ALL, not mb)

    def disabled_map(self, state: State) -> Dict[FieldKey, bool]:
        return {FieldKey.CONTEXT_MENU_ICON: not state.get(FieldKey.CONTEXT_MENU)}

    def disabled_langs(self, state: State) -> Set[str]:
        active = {FieldKey.OS_SITE, FieldKey.OS_HASH, FieldKey.YIFY_SITE, FieldKey.SUBSOURCE_SITE}
        enabled = {k for k in active if state.get(k)}
        disabled: Set[str] = set()
        for code, lang in languages.items():
            if any(p in enabled for p in lang.provider_incompatibility):
                disabled.add(code)
        return disabled


class Validator:
    def __init__(self, registry: Registry) -> None:
        self.registry = registry

    def validate_all(self, state: State) -> bool:
        for fk, meta in self.registry.fields.items():
            if not self._validate_field(fk, state.get(fk), meta.validators):
                return False
        return True

    def _validate_field(self, key: FieldKey, value: Any, validators: List[Callable[[Any], bool]]) -> bool:
        return all(validator(value) for validator in validators)
