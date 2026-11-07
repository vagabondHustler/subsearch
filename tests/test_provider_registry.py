from subsearch.runtime.config import defaults
from subsearch.runtime.config.defaults import ConfigKey
from subsearch.runtime.config.providers import (
    HEALTH_TRACKED_PROVIDERS,
    IMDB_DIAGNOSTIC_NAME,
    PROVIDER_DISPLAY_NAMES,
    PROVIDER_REGISTRY,
    SUPPORTED_PROVIDERS,
    Provider,
)

_DEFAULT_CONFIG = defaults.get_default_app_config()


def test_registry_covers_every_provider_enum_member() -> None:
    assert set(PROVIDER_REGISTRY) == set(Provider)


def test_descriptor_key_matches_its_provider_value() -> None:
    for provider, descriptor in PROVIDER_REGISTRY.items():
        assert descriptor.key == provider.value


def test_supported_providers_is_derived_from_registry() -> None:
    assert SUPPORTED_PROVIDERS == [provider.value for provider in Provider]


def test_display_names_cover_every_provider() -> None:
    assert set(PROVIDER_DISPLAY_NAMES) == {provider.value for provider in Provider}


def test_health_tracked_providers_include_imdb_and_all_providers() -> None:
    assert HEALTH_TRACKED_PROVIDERS == [IMDB_DIAGNOSTIC_NAME, *SUPPORTED_PROVIDERS]


def test_default_config_providers_match_supported_providers() -> None:
    providers = _DEFAULT_CONFIG["search"]["providers"]
    assert list(providers) == SUPPORTED_PROVIDERS
    assert all(enabled is True for enabled in providers.values())


def test_search_providers_config_key_points_at_provider_section() -> None:
    assert ConfigKey.SEARCH_PROVIDERS == "search.providers"
