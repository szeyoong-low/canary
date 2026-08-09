from fastapi import APIRouter, HTTPException
from httpx import codes
from pydantic import ValidationError

from ..display.output_models import ChartConfigModel
from ..global_types import DataProcessingError, ImplementationError
from .schemas import AssetPriceDailySchema, MarketCompositionSchema
from .tools import asset_price_daily, market_composition

router = APIRouter(prefix="/terminal")


@router.post("/asset-price-daily")
async def asset_price_daily_handler(args: AssetPriceDailySchema) -> ChartConfigModel:
    try:
        return await asset_price_daily.ainvoke(args.model_dump())
    except DataProcessingError as e:
        raise HTTPException(codes.UNPROCESSABLE_ENTITY, e.message)
    except ImplementationError as e:
        raise HTTPException(e.code, e.message)
    except ValidationError as e:
        raise HTTPException(codes.UNPROCESSABLE_ENTITY, str(e))


@router.post("/market-composition")
async def market_composition_handler(args: MarketCompositionSchema) -> ChartConfigModel:
    try:
        return await market_composition.ainvoke(args.model_dump())
    except DataProcessingError as e:
        raise HTTPException(codes.UNPROCESSABLE_ENTITY, e.message)
    except ImplementationError as e:
        raise HTTPException(e.code, e.message)
    except ValidationError as e:
        raise HTTPException(codes.UNPROCESSABLE_ENTITY, str(e))
