class DatabaseError(Exception):
    """Base, so a caller that does not care which failure it was can catch one
    thing. Never raised directly."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class NotFoundError(DatabaseError):
    """The row does not exist (or is soft deleted). 404"""


class StaleWriteError(DatabaseError):
    """The row exists but has been written since the caller read it. A lost
    update anomaly will happne if the write proceeds. 409 Conflict

    Carries the version now in force so the router can hand it back and the
    client can retry without a separate read.
    """

    def __init__(self, message: str, current_version: int):
        super().__init__(message)
        self.current_version = current_version


class MissingVersionError(DatabaseError):
    """An update that must be version-checked was called without a version.
    Client mistake, the request omitted `If-Match`, so 428 Precondition Required
    """
