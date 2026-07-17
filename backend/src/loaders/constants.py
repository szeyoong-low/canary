from typing import Literal

from ..global_constants import DATE_KEY, MetricGroup
from ..global_types import Columns

type ExternalAPI = Literal["FMP"]

type EndpointFMP = Literal["company-screener", "historical-price-eod/full"]

type ExternalEndpoint = EndpointFMP | Literal["TEST"]

METRIC_GROUP_KEYS: dict[MetricGroup, Columns] = {"asset-price-daily": [DATE_KEY]}

# Base metrics
# It would be better if we can use the schema of the data returned by the endpoint.
# Unfortunately, since each individual entity seeds itself, we will need to implement
# locking. It is safe to assume that versioned external APIs from for-profit data
# vendors will return consistent schemas.

ASSET_PRICE_DAILY_BASE_METRICS: Columns = {
    "open",
    "high",
    "low",
    "close",
    "volume",
    "change",
    "changePercent",
    "vwap",
}

MARKET_COMPOSITION_BASE_METRICS: Columns = {
    "marketCap",
    "beta",
    "price",
    "lastAnnualDividend",
    "volume",
}

METRIC_GROUP_BASE_METRICS: dict[MetricGroup, Columns] = {
    "asset-price-daily": ASSET_PRICE_DAILY_BASE_METRICS,
    "market-composition": MARKET_COMPOSITION_BASE_METRICS,
}
