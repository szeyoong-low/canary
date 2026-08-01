from collections.abc import Collection
from typing import Any

type Params = dict[str, Any]

type Column = str
type ColumnOptional = Column | None
type Columns = Collection[str]
type Entities = Collection[str]


async def as_awaitable[T](x: T) -> T:
    """Wrapper for already fulfilled awaitable"""
    return x


class DataProcessingError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ImplementationError(Exception):
    def __init__(self, code: int, message: str):
        super().__init__(message)
        self.message = message
        self.code = code
