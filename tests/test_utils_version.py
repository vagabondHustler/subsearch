import re

from data import __version__


def test_current() -> None:
    """
    test so to ensure that the src/subsearch/utils/version.current function returns a with the correct format
    """

    version_digits = "".join(re.findall(r"\d+", __version__))
    version_dots = "".join(re.findall(r"\.", __version__))

    assert version_digits.isnumeric() is True
    assert version_dots == ".."
