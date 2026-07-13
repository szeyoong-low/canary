from httpx import AsyncClient
from polars import LazyFrame
from starlette.datastructures import QueryParams

from .constants import METRIC_GROUP_KEYS, REQUEST_HEADERS
from .utility import _load_data
from ..validators.primitives import DateRangeModel

"""Data is left as-is in its long shape (yet to pivot on `symbol`) but sorted on its keys"""


async def load_asset_price_daily(
    http_client: AsyncClient,
    symbol: str,
    query_params: QueryParams,
) -> LazyFrame:

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
