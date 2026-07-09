from typing import Annotated

from fastapi import APIRouter, Query


TERMINAL_PREFIX = "/terminal"
router = APIRouter(prefix=TERMINAL_PREFIX)

# Path parameters
METRIC_PATH_PARAM = "/{metric}"
DISPLAY_PATH_PARAM = "/{display}"
TERMINAL_PATH = f"{METRIC_PATH_PARAM}{DISPLAY_PATH_PARAM}"


@router.get(TERMINAL_PATH)
def terminal_path_op(
    metric: str,
    display: str,
    analysis: Annotated[list[str], Query()],
    view: Annotated[list[str], Query()],
    symbol: Annotated[list[str], Query()],
):
    return {
        "metric": metric,
        "display": display,
        "analysis": analysis,
        "view": view,
        "symbol": symbol,
    }
