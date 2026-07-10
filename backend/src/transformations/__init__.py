from collections.abc import Awaitable, Callable, Iterable
from typing import Concatenate, Literal, TypedDict

from httpx import AsyncClient
from polars import LazyFrame
from starlette.datastructures import QueryParams

type ColumnIdentifier = str | Iterable[str]


"""
Metric generator contract

Inputs:
    - http_client: For loaders
    - symbol: Identifies the individual entity being processed
    - submetric: The specific dimension of analysis
    - query_params: Raw query parameters captured by the path handler, to be
        validated with a Pydantic model

Output: Awaitable LazyFrame with only three columns: [symbol, <key>, <submetric>]
    - symbol: As per input. Column must be named symbol.
    - key: Column may be named anything. This name is declared in METRIC_GEN.
    - submetric: The metric that forms the basis of all further analysis.
        Column must be named after itself.
"""
type MetricGen = Callable[[AsyncClient, str, str, QueryParams], Awaitable[LazyFrame]]

type Metric = Literal["share-price-eod"]


class MetricGenParams(TypedDict):
    function: MetricGen
    key: str


"""
Contract of the pipeline's individual and collective transformations

Functions that take a LazyFrame (optimised DataFrame) and arbitrary arguments
and returns a LazyFrame. P is a ParamSpec.
"""

type Transform[**P] = Callable[Concatenate[LazyFrame, P], LazyFrame]

"""
Individual transformation contract

Inputs:
    - data: LazyFrame as returned by metric generator
    - submetric: The specific dimension of analysis
    - key: Column to align on
    - query_params: Raw query parameters captured by the path handler, to be
        validated with a Pydantic model

Side effects:
    - No additional data fetches may be made

Output: LazyFrame which is an extension of the input. The columns in the input
    may not be mutated. New columns must be alinged on the same key. The new columns
"""
