from collections.abc import Collection
from typing import Literal

from ..constants import DATE_KEY, MetricGroup
from ..types import Columns

type ExternalAPI = Literal["FMP"]

type EndpointFMP = Literal["historical-price-eod/full"]

type ExternalEndpoint = EndpointFMP | Literal["TEST"]

METRIC_GROUP_KEYS: dict[MetricGroup, Columns] = {"asset-price-daily": [DATE_KEY]}

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
