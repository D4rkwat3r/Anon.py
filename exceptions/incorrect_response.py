from .anon_exception import AnonException


class IncorrectResponse(AnonException):
    def __init__(self):
        super().__init__("IncorrectResponse", "Unable to decode API response")
