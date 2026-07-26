from fastapi import APIRouter, HTTPException, Request
from httpx import codes
from pydantic import ValidationError

from ..display.charts import DisplayFunctionName
from ..display.output_models import ChartConfigModel
from ..global_types import DataProcessingError, ImplementationError
from .models import (
    ColumnOptionalQueryParam,
    ColumnQueryParam,
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

    try:
        return await asset_price_daily.ainvoke(
            {
                "display": display,
                "analysis": analysis,
                "symbol": symbol,
                **AssetPriceDailyAPI.validate_query_params(
                    request.query_params
                ).model_dump(exclude_unset=True),
            }
        )
    except DataProcessingError as e:
        raise HTTPException(codes.UNPROCESSABLE_ENTITY, e.message)
    except ImplementationError as e:
        raise HTTPException(e.code, e.message)
    except ValidationError as e:
        raise HTTPException(codes.UNPROCESSABLE_ENTITY, str(e))


@router.get(_get_terminal_path("market-composition"))
async def market_composition_handler(
    display: DisplayFunctionName,
    analysis: SetQueryParam,
    drilldown: MarketDrilldownQueryParam,
    request: Request,
    aggregate_col: ColumnQueryParam,
    colour_col: ColumnOptionalQueryParam = None,
) -> ChartConfigModel:

    try:
        return await market_composition.ainvoke(
            {
                "display": display,
                "analysis": analysis,
                "drilldown": drilldown,
                "aggregate_col": aggregate_col,
                "colour_col": colour_col,
            }
        )
    except DataProcessingError as e:
        raise HTTPException(codes.UNPROCESSABLE_ENTITY, e.message)
    except ImplementationError as e:
        raise HTTPException(e.code, e.message)
    except ValidationError as e:
        raise HTTPException(codes.UNPROCESSABLE_ENTITY, str(e))
