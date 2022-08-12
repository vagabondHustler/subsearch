from src.subsearch.utils import current_user


def test_got_key() -> None:
    """
    test to ensure that the src/subsearch/utils/current_user.get_key function returns boolean
    """
    assert current_user.got_key() or current_user.got_key() is False


def test_is_exe() -> None:
    """
    test to ensure that the src/subsearch/utils/current_user.is_exe function returns boolean
    """
    assert current_user.check_is_exe() or current_user.check_is_exe() is False
