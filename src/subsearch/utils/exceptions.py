class Error(Exception):
    """Base class for exceptions in subsearch"""

    pass


class ProviderError(Error):
    """Base class for errors raised by subtitle providers."""

    pass


class CaptchaError(ProviderError):
    """Error raised when a captcha challenge is encountered."""

    def __init__(self, message: str = "Captcha challenge encountered"):
        super().__init__(message)


class ProviderNotImplemented(ProviderError):
    """Error raised when using an unsupported subtitle provider."""

    def __init__(self, message: str = "This provider is not implemented"):
        super().__init__(message)


class MultipleInstancesError(Error):
    """Error raised when multiple instances of the application are running"""

    def __init__(self, mutex_name: str):
        message = f"Multiple instances of the application are running. Mutex '{mutex_name}' is already acquired."
        super().__init__(message)
