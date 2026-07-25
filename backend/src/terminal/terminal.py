from fastapi import APIRouter, Request

from ..display.charts import DisplayFunctionName
from ..display.output_models import ChartConfigModel
from .models import (
    ColumnQueryParam,
    ColumnOptionalQueryParam,
    EntityQueryParam,
    MarketDrilldownQueryParam,
    SetQueryParam,
)
from .schemas import AssetPriceDailyAPI
from .tools import asset_price_daily, market_composition
from .utility import _get_terminal_path

router = APIRouter(prefix="/terminal")


@router.get(_get_terminal_path("asset-price-daily"))
async def asset_price_daily_handler(
    display: DisplayFunctionName,
    analysis: SetQueryParam,
    symbol: EntityQueryParam,
    request: Request,
) -> ChartConfigModel:
    print(AssetPriceDailyAPI.model_fields)
    return await asset_price_daily(
        display,
        analysis,
        symbol,
        **AssetPriceDailyAPI.validate_query_params(request.query_params).model_dump(
            exclude_unset=True
        ),
    )


@router.get(_get_terminal_path("market-composition"))
async def market_composition_handler(
    display: DisplayFunctionName,
    analysis: SetQueryParam,
    drilldown: MarketDrilldownQueryParam,
    request: Request,
    aggregate_col: ColumnQueryParam,
    colour_col: ColumnOptionalQueryParam = None,
) -> ChartConfigModel:

    return await market_composition(
        display, analysis, drilldown, aggregate_col, colour_col
    )
