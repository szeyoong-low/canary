from typing import Annotated

from fastapi import APIRouter, Query

router = APIRouter(prefix="/terminal")

# Path parameters
METRIC_GROUP_PATH_PARAM = "/{metric_group}"
DISPLAY_PATH_PARAM = "/{display}"
TERMINAL_PATH = f"{METRIC_GROUP_PATH_PARAM}{DISPLAY_PATH_PARAM}"


@router.get(TERMINAL_PATH)
def terminal_handler(
    metric_group: str,
    display: str,
    analysis: Annotated[list[str], Query()],
    symbol: Annotated[list[str], Query()],
):
    return {
        "metric_group": metric_group,
        "display": display,
        "analysis": analysis,
        "symbol": symbol,
    }
