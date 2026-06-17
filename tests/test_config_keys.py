import pytest

from subsearch.io.nested_dict import get_keys_recursively
from subsearch.runtime.config import defaults
from subsearch.runtime.config.defaults import ConfigKey

# Runtime health counters Subsearch manages itself, not user-facing settings. They are
# created per provider, so they have no stable ConfigKey and are excluded from the
# "every leaf is keyed" guard below.
UNKEYED_RUNTIME_STATE_PREFIX = "diagnostics.provider_diagnostics"

_DEFAULT_CONFIG = defaults.get_default_app_config()


def _resolve(key: str) -> object:
    value: object = _DEFAULT_CONFIG
    for part in key.split("."):
        value = value[part]  # type: ignore[index]
    return value


def _is_leaf(key: str) -> bool:
    return not isinstance(_resolve(key), dict)


@pytest.mark.parametrize("config_key", list(ConfigKey))
def test_every_config_key_resolves_against_defaults(config_key: ConfigKey) -> None:
    try:
        _resolve(config_key)
    except KeyError, TypeError:
        pytest.fail(f"{config_key.name} ({config_key.value}) does not exist in the default config")


def test_every_config_leaf_is_covered_by_a_config_key() -> None:
    members = {str(member) for member in ConfigKey}
    leaves = [key for key in get_keys_recursively(_DEFAULT_CONFIG) if _is_leaf(key)]
    uncovered = [
        leaf
        for leaf in leaves
        if not leaf.startswith(UNKEYED_RUNTIME_STATE_PREFIX)
        and not any(leaf == member or leaf.startswith(f"{member}.") for member in members)
    ]
    assert uncovered == [], f"config leaves without a ConfigKey: {uncovered}"


def test_config_key_values_are_unique() -> None:
    values = [member.value for member in ConfigKey]
    assert len(values) == len(set(values))
