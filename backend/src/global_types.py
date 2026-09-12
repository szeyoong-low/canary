from collections.abc import Collection
from typing import Any

type Params = dict[str, Any]

type Column = str
type ColumnOptional = Column | None
type Columns = Collection[str]
type Entities = Collection[str]


type RowObjectDataset = list[Params]  #  Polars `to_dicts`
type ColumnarDataset = dict[str, list]  # Polars `to_dict`
# Columnar preferred: no repeated key strings, easier CSV conversion
type DatasetType = RowObjectDataset | ColumnarDataset


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
