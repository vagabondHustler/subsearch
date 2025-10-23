from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional


class FieldKey(Enum):
    API_CALL_LIMIT = auto()
    REQ_CONNECT_TIMEOUT = auto()
    REQ_READ_TIMEOUT = auto()
    ACCEPT_THRESHOLD = auto()
    OPEN_ON_NO_MATCHES = auto()
    ALWAYS_OPEN = auto()
    AUTO_DOWNLOADS = auto()
    CONTEXT_MENU = auto()
    CONTEXT_MENU_ICON = auto()
    EXT_AVI = auto()
    EXT_MP4 = auto()
    EXT_MKV = auto()
    EXT_MPG = auto()
    EXT_MPEG = auto()
    EXT_MOV = auto()
    EXT_RM = auto()
    EXT_VOB = auto()
    EXT_WMV = auto()
    EXT_FLV = auto()
    EXT_3GP = auto()
    EXT_3G2 = auto()
    EXT_SWF = auto()
    EXT_MSWMM = auto()
    SYSTEM_TRAY = auto()
    SUMMARY_NOTIFICATION = auto()
    SHOW_TERMINAL = auto()
    SINGLE_INSTANCE = auto()
    OS_SITE = auto()
    OS_HASH = auto()
    YIFY_SITE = auto()
    SUBSOURCE_SITE = auto()
    CURRENT_LANGUAGE = auto()
    HEARING_IMPAIRED = auto()
    NON_HEARING_IMPAIRED = auto()
    ONLY_FOREIGN_PARTS = auto()
    RENAME = auto()
    MOVE_BEST = auto()
    MOVE_ALL = auto()
    TARGET_PATH = auto()
    PATH_RESOLUTION = auto()


class WidgetType(Enum):
    BOOL = auto()
    INT = auto()
    SLIDER = auto()
    RADIO_PICKER = auto()
    RADIO_MOVE = auto()
    TEXT = auto()
    SELECT = auto()
    LANGUAGE = auto()


class CardKey(Enum):
    PROVIDER_NETWORKS = auto()
    DOWNLOAD = auto()
    CONTEXT_MENU = auto()
    FILE_EXT = auto()
    APP = auto()
    PROVIDERS = auto()
    SUBTITLE_STYLE = auto()
    HANDLE_DOWNLOADED = auto()
    ABOUT = auto()


class ScreenKey(Enum):
    APP = auto()
    SEARCH = auto()
    DOWNLOAD = auto()
    ABOUT = auto()


class LayoutKind(Enum):
    STACK = "stack"
    ROW = "row"
    GRID = "grid"
    EXTENSIONS = "extensions"


@dataclass
class LayoutSpec:
    kind: LayoutKind
    fields: List[FieldKey]
    spacing: Optional[int] = None
    col: Optional[Dict[str, int]] = None
    title: Optional[str] = None


@dataclass
class FieldMeta:
    key: FieldKey
    label: str
    tip: Optional[str]
    widget: WidgetType
    default: Any
    validators: List[Callable[[Any], bool]] = field(default_factory=list)


@dataclass
class CardMetaData:
    title: str
    icon: str
    fields: List[FieldKey]
    layout: Optional[List[LayoutSpec]] = None
    spacing_override: Optional[int] = None
