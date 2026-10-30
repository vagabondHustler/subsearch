from dataclasses import dataclass
from enum import StrEnum


class Provider(StrEnum):
    OPENSUBTITLES = "opensubtitles"
    YIFYSUBTITLES = "yifysubtitles"
    SUBSOURCE = "subsource"
    TVSUBTITLES = "tvsubtitles"
    GESTDOWN = "gestdown"


@dataclass(frozen=True, slots=True)
class ProviderDescriptor:
    provider: Provider
    display_name: str
    supports_movies: bool
    supports_tvseries: bool
    requires_api_key: bool

    @property
    def key(self) -> str:
        return self.provider.value


PROVIDER_REGISTRY: dict[Provider, ProviderDescriptor] = {
    Provider.OPENSUBTITLES: ProviderDescriptor(
        provider=Provider.OPENSUBTITLES,
        display_name="Opensubtitles",
        supports_movies=True,
        supports_tvseries=True,
        requires_api_key=False,
    ),
    Provider.YIFYSUBTITLES: ProviderDescriptor(
        provider=Provider.YIFYSUBTITLES,
        display_name="Yifysubtitles",
        supports_movies=True,
        supports_tvseries=False,
        requires_api_key=False,
    ),
    Provider.SUBSOURCE: ProviderDescriptor(
        provider=Provider.SUBSOURCE,
        display_name="Subsource",
        supports_movies=True,
        supports_tvseries=True,
        requires_api_key=True,
    ),
    Provider.TVSUBTITLES: ProviderDescriptor(
        provider=Provider.TVSUBTITLES,
        display_name="Tvsubtitles",
        supports_movies=False,
        supports_tvseries=True,
        requires_api_key=False,
    ),
    Provider.GESTDOWN: ProviderDescriptor(
        provider=Provider.GESTDOWN,
        display_name="Gestdown",
        supports_movies=False,
        supports_tvseries=True,
        requires_api_key=False,
    ),
}

# Health-tracked names include imdb, whose URL resolution is diagnosed alongside the
# subtitle providers even though it is not itself a selectable provider.
IMDB_DIAGNOSTIC_NAME = "imdb"

SUPPORTED_PROVIDERS: list[str] = [descriptor.key for descriptor in PROVIDER_REGISTRY.values()]

HEALTH_TRACKED_PROVIDERS: list[str] = [IMDB_DIAGNOSTIC_NAME, *SUPPORTED_PROVIDERS]

PROVIDER_DISPLAY_NAMES: dict[str, str] = {
    descriptor.key: descriptor.display_name for descriptor in PROVIDER_REGISTRY.values()
}
