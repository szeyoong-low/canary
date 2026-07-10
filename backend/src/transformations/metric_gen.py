from httpx import AsyncClient
from polars import all, col, LazyFrame
from starlette.datastructures import QueryParams

from . import Metric, MetricGenParams
from ..loaders import load_data, REQUEST_HEADERS
from .models.primitives import DateRangeModel


SHARE_PRICE_EOD_SUBMETRIC: list[str] = [
    "open",
    "high",
    "low",
    "close",
    "volume",
    "change",
    "changePercent",
    "vwap",
]

SHARE_PRICE_EOD_KEY = "date"


async def share_price_eod(
    http_client: AsyncClient,
    symbol: str,
    submetric: str,
    query_params: QueryParams,
) -> LazyFrame:
    validated_params: DateRangeModel = DateRangeModel.model_validate(query_params)

    # I decided that it is better style to have the metric and submetric sit
    # together as path parameters instead of having the submetric be a query
    # parameter. What this forgoes is the ability to use a Pydantic model for
    # type checking against a literal.
    if submetric not in SHARE_PRICE_EOD_SUBMETRIC:
        raise ValueError(f"{submetric} not one of {SHARE_PRICE_EOD_SUBMETRIC}")

    # It is unnecessary to drop unused columns as Polars lazy API will cull them
    # eventually. There is no risk of column name clashes down the road. As per
    # the contract, anything other the three columns can be assumed to not exist.
    # If a later transformation creates a column with the same name, it will simply
    # overwrite it.
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

    return data.select(
        col(SHARE_PRICE_EOD_KEY),
        all().exclude(SHARE_PRICE_EOD_KEY).name.prefix(f"{symbol}_".upper()),
    )


METRIC_GEN: dict[Metric, MetricGenParams] = {
    "share-price-eod": {
        "function": share_price_eod,
        "key": SHARE_PRICE_EOD_KEY,
    },
}
