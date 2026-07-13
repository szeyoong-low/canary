from collections.abc import Collection
from typing import Literal, Callable

from polars import LazyFrame

from ..constants import MetricGroup
from ..dependencies import get_environment
from .normalise import _normalise_fmp
from ..types import Columns, Params

type ExternalAPI = Literal["FMP"]

type EndpointFMP = Literal["historical-price-eod/full"]

type ExternalEndpoint = EndpointFMP | Literal["TEST"]

# Dispatch tables
# Kept as a callable to achieve pseudo-lazy evaluation so that there is no
# coupling with the test suite, which must still evaluate it when importing.
REQUEST_HEADERS: dict[ExternalAPI, Callable[[], Params]] = {
    "FMP": (lambda: {"apikey": get_environment().fmp_api_key}),
}

# The base URLs must have a trailing slash
BASE_URL: dict[ExternalAPI, Callable[[], str]] = {
    "FMP": (lambda: get_environment().fmp_base_url),
}

NORMALISER: dict[ExternalAPI, Callable[[LazyFrame], LazyFrame]] = {
    "FMP": _normalise_fmp,
}

# Keys of all data loaded for a specific metric group
METRIC_GROUP_KEYS: dict[MetricGroup, Columns] = {"asset-price-daily": ["date"]}

# Base metrics
# It would be better if we can use the schema of the data returned by the endpoint.
# Unfortunately, since each individual entity seeds itself, we will need to implement
# locking. It is safe to assume that versioned external APIs from for-profit data
# vendors will return consistent schemas.

ASSET_PRICE_DAILY_BASE_METRICS: Collection[str] = {
    "open",
    "high",
    "low",
    "close",
    "volume",
    "change",
    "changePercent",
    "vwap",
}

METRIC_GROUP_BASE_METRICS: dict[MetricGroup, Collection[str]] = {
    "asset-price-daily": ASSET_PRICE_DAILY_BASE_METRICS,
}
