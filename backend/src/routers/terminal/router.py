from typing import Annotated

from fastapi import APIRouter, Query, Request
from httpx import AsyncClient
from polars import LazyFrame
from starlette.datastructures import QueryParams

from ...transformations import Metric
from ...transformations.metric_gen import METRIC_GEN


TERMINAL_PREFIX = "/terminal"
router = APIRouter(prefix=TERMINAL_PREFIX)

# Path parameters
METRIC_PATH_PARAM = "/{metric}"
DISPLAY_PATH_PARAM = "/{display}"
TERMINAL_PATH = f"{METRIC_PATH_PARAM}{DISPLAY_PATH_PARAM}"


@router.get(TERMINAL_PATH)
async def terminal_path_op(
    metric: Metric,
    display: str,
    analysis: Annotated[list[str], Query()],
    view: Annotated[list[str], Query()],
    symbol: Annotated[list[str], Query()],
    request: Request,
):
    query_params: QueryParams = request.query_params

    async with AsyncClient(follow_redirects=True) as client:
        for s in symbol:
            init_data: LazyFrame = await METRIC_GEN[metric](client, s, query_params)
            print(init_data.collect())

    return {
        "metric": metric,
        "display": display,
        "analysis": analysis,
        "view": view,
        "symbol": symbol,
    }
