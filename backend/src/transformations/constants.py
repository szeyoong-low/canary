from collections.abc import Awaitable, Callable

from httpx import AsyncClient
from polars import LazyFrame

from ..global_types import Columns
from ..transformations.models import Transformation

"""
Contract of transformation implementations

Args:
    - data (Awaitable LazyFrame)
    - keys (Columns): Columns to align on
    - transformation (Transformation): Specification of the transformation,
        including its name, dependencies, and other parameters. All have been
        validated except for whether dependencies are of the correct `Scope`.
    - http_client (AsyncClient): For loaders

Returns: Awaitable LazyFrame with the transformation and all its dependencies
        present as columns named `<depends>/<transformation name>` or
        `<base metric>` alinged on `keys`. Existing columns are unmodified.
        Must be defined with the async keyword.
"""

type TransformationFunction = Callable[
    [Awaitable[LazyFrame], Columns, Transformation, AsyncClient],
    Awaitable[LazyFrame],
]

type TransformationDispatch = dict[str, TransformationFunction]
