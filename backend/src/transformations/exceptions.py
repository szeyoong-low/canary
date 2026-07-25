from ..global_types import DataProcessingError


class AnalysisError(DataProcessingError):
    def __init__(self, message):
        super().__init__(message)
