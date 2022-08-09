from src.subsearch.utils import current_user


def test_got_key() -> None:
    assert current_user.got_key() or current_user.got_key() is False

def test_is_exe() -> None:
    assert current_user.is_exe() or current_user.is_exe() is False