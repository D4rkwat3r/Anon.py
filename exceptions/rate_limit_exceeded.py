from .anon_exception import AnonException


class RateLimitExceeded(AnonException):
    def __init__(self, code: str, message: str, reset: int = None):
        super().__init__(code, message)
        self.reset = reset
