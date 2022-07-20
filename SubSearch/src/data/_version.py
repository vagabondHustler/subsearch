_VERSION = "2.6.12"


def current_version(version: str = _VERSION) -> str:
    """Summary

    Patch release (0.0.1 -> 0.0.2): bug fixes
    Minor release (0.1.0 -> 0.2.0): larger bug fixes or new features
    Major release (1.0.0 -> 2.0.0): stable releases

    Args:
        version (str, optional): _description_. Defaults to _VERSION.

    Returns:
        str: version
    """
    return version


current_version()
