class RocketException(Exception):
    def __init__(self, error: str, error_type: str):
        self.error = error
        self.error_type = error_type
        super().__init__(error)
