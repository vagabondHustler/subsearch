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
        error_type = f"Multiple instances of the application are running."
        error_msg = f"Unable to acquire mutex '{mutex_name}' because it's already locked. Please close any other instances of the application before launching a new one."
        additional_info = "If you need to run multiple instances, you can adjust your app settings to allow this, but be aware that it's not recommended'."
        message = f"{error_type}\n{error_msg}\n{additional_info}"

        super().__init__(message)
