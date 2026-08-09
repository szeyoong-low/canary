from httpx import AsyncClient
from polars import LazyFrame

from ..global_types import Params
from ..validators.primitives import DateRange
from . import models
from .constants import METRIC_GROUP_KEYS
from .dispatch import REQUEST_HEADERS
from .utility import _load_data

"""Data is left as-is in its long shape (yet to pivot on `symbol`)"""

LIMIT_NUM_ENTRIES: int = 200


async def load_asset_price_daily(
    http_client: AsyncClient,
    symbol: str,
    params: Params,
) -> LazyFrame:
    """Data is sorted earliest to latest"""

    date_range: DateRange = DateRange.model_validate(params)

    return (
        await _load_data(
            http_client=http_client,
            external_api="FMP",
            endpoint="historical-price-eod/full",
            query_params={
                "symbol": symbol,
                "from": date_range.start_date,
                "to": date_range.end_date,
            },
            headers=REQUEST_HEADERS["FMP"](),
        )
    ).sort(by=METRIC_GROUP_KEYS["asset-price-daily"], nulls_last=True)


async def load_market_composition(
    http_client: AsyncClient,
    params: Params,
) -> LazyFrame:
    """Data is sorted in descending order of market capitalisation"""

    filters: models.MarketCompositionFilters = (
        models.MarketCompositionFilters.model_validate(params)
    )

    return await _load_data(
        http_client=http_client,
        external_api="FMP",
        endpoint="company-screener",
        query_params={
            "country": filters.country,
            "industry": filters.industry,
            "sector": filters.sector,
            "exchange": filters.exchange,
            "isEtf": filters.category == "etf",
            "isFund": filters.category == "fund",
            "isActivelyTrading": True,
            "limit": LIMIT_NUM_ENTRIES,
            "includeAllShareClasses": False,
        },
        headers=REQUEST_HEADERS["FMP"](),
    )
