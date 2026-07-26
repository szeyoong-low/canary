from collections.abc import Collection
from typing import Any, TypeVar

type Params = dict[str, Any]

type Column = str
type ColumnOptional = Column | None
type Columns = Collection[str]
type Entities = Collection[str]

T = TypeVar("T")


async def as_awaitable(x: T) -> T:
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
