from collections.abc import Awaitable, Callable
from typing import Literal, TypedDict

from httpx import AsyncClient
from polars import LazyFrame
from starlette.datastructures import QueryParams

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
