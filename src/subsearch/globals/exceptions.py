class Error(Exception):
    pass


class ProviderError(Error):
    pass


class CaptchaError(ProviderError):
    def __init__(self, message: str = "Captcha challenge encountered") -> None:
        super().__init__(message)


class ProviderNotImplemented(ProviderError):
    def __init__(self, message: str = "This provider is not implemented") -> None:
        super().__init__(message)


class MultipleInstancesError(Error):
    def __init__(self, mutex_name: str) -> None:
        error_msg = f"Another instance of the application is already running. Please close any other instances of the application before launching a new one."
        super().__init__(error_msg)
