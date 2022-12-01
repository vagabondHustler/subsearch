from src.subsearch.utils import raw_registry


def test_got_key() -> None:
    """
    test to ensure that the src/subsearch/utils/raw_registry.get_key function returns boolean
    """
    assert raw_registry.registry_key_exists() or raw_registry.registry_key_exists() is False
