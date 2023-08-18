import re

from subsearch.data import __version__


def test_current() -> None:
    version_digits = "".join(re.findall(r"\d+", __version__))
    assert version_digits.isnumeric() is True
