class ApiError(Exception):
    status: int
    message: str

    def __init__(self, status: int, message: str) -> None:
        self.status = status
        self.message = message
        super().__init__(f"{status} {message}")


class DataValidationError(Exception):
    pass


class NetworkError(Exception):
    pass
