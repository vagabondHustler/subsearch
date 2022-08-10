import re

from src.subsearch.utils import version


def test_current() -> None:
    """
    test to ensure that the version is of the correct format
    """
    c_version = version.current()
    version_digits = "".join(re.findall(r"\d+", c_version))
    version_text = "".join(re.findall(r"[a-zA-Z]+", c_version))
    version_dots = "".join(re.findall(r"\.", c_version))

    assert version_digits.isnumeric() is True
    assert version_text == "v"
    assert version_dots == ".."
