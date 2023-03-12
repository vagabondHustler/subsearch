from src.subsearch.utils import io_winreg


def test_got_key() -> None:
    """
    test to ensure that the src/subsearch/utils/io_winreg.get_key function returns boolean
    """
    assert io_winreg.registry_key_exists() or io_winreg.registry_key_exists() is False
