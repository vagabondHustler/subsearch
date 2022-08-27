class Error(Exception):
    """Base class for exceptions in subsearch"""

    pass


class ProviderError(Error):
    """Base class for exceptions by providers"""

    pass


class CaptchaError(ProviderError):
    """Exception raised by provider when captcha is detected"""
