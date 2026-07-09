from httpx import AsyncClient
from polars import LazyFrame

from ..loaders import load_data, REQUEST_HEADERS
from ..models.primitive_models import DateRangeModel
from ..utility.types import params


async def share_price_eod(
    http_client: AsyncClient, symbol: str, query_params: params
) -> LazyFrame:
    validated_params: DateRangeModel = DateRangeModel.model_validate(query_params)

    return await load_data(
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
