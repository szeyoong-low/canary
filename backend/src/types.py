from collections.abc import Collection
from typing import Any, TypeVar

type Params = dict[str, Any]

type Columns = str | Collection[str]

T = TypeVar("T")


async def as_awaitable(x: T) -> T:
    """Wrapper for already fulfilled awaitable"""
    return x
