from collections.abc import Callable

from httpx import AsyncClient
from polars import LazyFrame

from ..utility.types import params

"""
Metric generator contract

Inputs:
    - http_client: for loaders
    - symbol: identifies the individual entity being processed
    - query_params: raw query parameters captured by the path handler, to be
        validated with a Pydantic model

Output: LazyFrame with only three columns: [symbol, key, value (metric)]
    - symbol: as per input
    - key-value: the metric that forms the basis of all further analysis
"""
type MetricGen = Callable[[AsyncClient, str, params], LazyFrame]
