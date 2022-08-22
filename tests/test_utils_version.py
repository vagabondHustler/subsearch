import re

from subsearch.data import __version__


def test_current() -> None:
    """
    test so to ensure that the src/subsearch/utils/version.current function returns a with the correct format
    """

    version_digits = "".join(re.findall(r"\d+", __version__))
    version_dots = "".join(re.findall(r"\.", __version__))

    assert version_digits.isnumeric() is True
    if "-rc" or "-beta" or "-alpha" in __version__:
        assert version_dots == "..."
    else:
        assert version_dots == ".."
