import re

from src.subsearch.utils import version


def test_current() -> None:
    c_version = version.current()
    version_digits = "".join(re.findall(r"\d+", c_version))

    assert version_digits.isnumeric() is True
