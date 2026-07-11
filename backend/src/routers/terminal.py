from typing import Annotated

from fastapi import APIRouter, Query

from .utility import _get_terminal_path


router = APIRouter(prefix="/terminal")


@router.get(_get_terminal_path("asset-price-daily"))
def asset_price_daily_handler(
    display: str,
    analysis: Annotated[list[str], Query()],
    symbol: Annotated[list[str], Query()],
):
    return {
        "metric_group": "asset-price-daily",
        "display": display,
        "analysis": analysis,
        "symbol": symbol,
    }
