from src.subsearch.utils import current_user


def test_got_key() -> None:
    """
    test to ensure that the src/subsearch/utils/current_user.get_key function returns boolean
    """
    assert current_user.registry_key_exists() or current_user.registry_key_exists() is False


def test_is_exe() -> None:
    """
    test to ensure that the src/subsearch/utils/current_user.is_exe function returns boolean
    """
    assert current_user.running_from_exe() or current_user.running_from_exe() is False
