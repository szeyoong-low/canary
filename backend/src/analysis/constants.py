from collections.abc import Awaitable, Callable

from httpx import AsyncClient
from polars import LazyFrame

from ..analysis.models import AnalysisFunction
from ..global_types import Columns, Params

"""
Contract of analysis function implementations

Args:
    - data (Awaitable LazyFrame)
    - analysis function (AnalysisFunction): Specification of the analysis function,
        including its name, dependencies, and other parameters. All have been
        validated except for whether dependencies are of the correct `Scope`.
    - keys (Columns): Columns to align on
    - shared_params (Params): Global parameters shared across all analysis functions.
    - http_client (AsyncClient): For loaders

Returns: Awaitable LazyFrame with the analysis function and all its dependencies
        present as columns alinged on `keys`. Existing columns are unmodified.
        Must be defined with the async keyword.
"""

type AnalysisFunctionExecuter[T: AnalysisFunction] = Callable[
    [Awaitable[LazyFrame], T, Columns, Params, AsyncClient],
    Awaitable[LazyFrame],
]

type AnalysisFunctionDispatch = dict[str, AnalysisFunctionExecuter]
