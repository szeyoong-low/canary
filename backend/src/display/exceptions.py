from ..global_types import DataProcessingError


class DisplayError(DataProcessingError):
    def __init__(self, message):
        super().__init__(message)
