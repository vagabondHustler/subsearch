class Error(Exception):
    """Base class for exceptions in subsearch"""
    pass


class ProviderError(Error):
    """Base class for errors raised by subtitle providers."""
    pass

class CaptchaError(ProviderError):
    """Error raised when a captcha challenge is encountered."""
    def __init__(self, message="Captcha challenge encountered"):
        super().__init__(message)

class ProviderNotImplemented(ProviderError):
    """Error raised when using an unsupported subtitle provider."""
    def __init__(self, message="This provider is not implemented"):
        super().__init__(message)