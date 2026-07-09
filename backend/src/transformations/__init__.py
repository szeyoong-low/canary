from collections.abc import Awaitable, Callable
from typing import Literal

from httpx import AsyncClient
from polars import LazyFrame
from starlette.datastructures import QueryParams

"""
Metric generator contract

Inputs:
    - http_client: for loaders
    - symbol: identifies the individual entity being processed
    - submetric: the specific dimension of analysis
    - query_params: raw query parameters captured by the path handler, to be
        validated with a Pydantic model

Output: Awaitable LazyFrame with only three columns: [symbol, key, value (metric)]
    - symbol: as per input
    - key-value: the metric that forms the basis of all further analysis
"""
type MetricGen = Callable[[AsyncClient, str, str, QueryParams], Awaitable[LazyFrame]]

type Metric = Literal["share-price-eod"]
