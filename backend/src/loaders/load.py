from httpx import AsyncClient
from polars import LazyFrame
from starlette.datastructures import QueryParams

from . import models
from .constants import METRIC_GROUP_KEYS
from .dispatch import REQUEST_HEADERS
from .utility import _load_data
from ..validators.primitives import DateRangeModel

"""Data is left as-is in its long shape (yet to pivot on `symbol`)"""

LIMIT_NUM_ENTRIES: int = 200


async def load_asset_price_daily(
    http_client: AsyncClient,
    symbol: str,
    query_params: QueryParams,
) -> LazyFrame:
    """Data is sorted earliest to latest"""

    validated_params: DateRangeModel = DateRangeModel.model_validate(query_params)

    return (
        await _load_data(
            http_client=http_client,
            external_api="FMP",
            endpoint="historical-price-eod/full",
            query_params={
                "symbol": symbol,
                "from": validated_params.start_date,
                "to": validated_params.end_date,
            },
            headers=REQUEST_HEADERS["FMP"](),
        )
    ).sort(by=METRIC_GROUP_KEYS["asset-price-daily"], nulls_last=True)


async def load_market_composition(
    http_client: AsyncClient,
    query_params: QueryParams,
) -> LazyFrame:
    """Data is sorted in descending order of market capitalisation"""

    validated_params: models.MarketComposition = (
        models.MarketComposition.validate_query_params(query_params)
    )

    return await _load_data(
        http_client=http_client,
        external_api="FMP",
        endpoint="company-screener",
        query_params={
            "country": validated_params.country,
            "industry": validated_params.industry,
            "sector": validated_params.sector,
            "exchange": validated_params.exchange,
            "isEtf": validated_params.category == "etf",
            "isFund": validated_params.category == "fund",
            "isActivelyTrading": True,
            "limit": LIMIT_NUM_ENTRIES,
            "includeAllShareClasses": False,
        },
        headers=REQUEST_HEADERS["FMP"](),
    )
