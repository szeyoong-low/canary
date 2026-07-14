from collections.abc import Callable
from typing import Awaitable

from httpx import AsyncClient
from polars import LazyFrame
from starlette.datastructures import QueryParams

from ..global_types import Columns

"""
Contract of transformations

Args:
    - data (Awaitable LazyFrame)
    - keys (Columns): Columns to align on
    - depends (str | None): Immediate preceding dependency transformation. None
        if it is a base metric.
    - query_params (QueryParams): Raw query parameters captured by the path
        handler, to be validated with a Pydantic model
    - http_client (AsyncClient): For loaders

Returns: Awaitable LazyFrame with the transformation and all its dependencies
         present as columns named `<depends>/<transformation name>` or
         `<base metric>` alinged on `keys`. Existing columns are unmodified.
         
         Must be defined with the async keyword.
"""

type Transformation = Callable[
    [Awaitable[LazyFrame], Columns, str | None, QueryParams, AsyncClient],
    Awaitable[LazyFrame],
]

type TransformationDispatch = dict[str, Transformation]
