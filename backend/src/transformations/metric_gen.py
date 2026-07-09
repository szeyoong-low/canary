from httpx import AsyncClient
from polars import LazyFrame, lit
from starlette.datastructures import QueryParams

from . import SYMBOL_IDENTIFIER
from ..loaders import load_data, REQUEST_HEADERS
from ..models.primitive_models import DateRangeModel


async def share_price_eod(
    http_client: AsyncClient, symbol: str, query_params: QueryParams
) -> LazyFrame:
    validated_params: DateRangeModel = DateRangeModel.model_validate(query_params)

    data: LazyFrame = await load_data(
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

    return data.with_columns(lit(symbol).alias(SYMBOL_IDENTIFIER))

METRIC_GEN: dict[Metric, MetricGen] = {
    "share-price-eod": share_price_eod,
}
