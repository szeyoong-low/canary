from typing import Annotated

from asyncio import gather
from fastapi import APIRouter, Query, Request
from httpx import AsyncClient
from polars import concat, LazyFrame
from starlette.datastructures import QueryParams

from ...transformations import Metric
from ...transformations.metric_gen import METRIC_GEN


TERMINAL_PREFIX = "/terminal"
router = APIRouter(prefix=TERMINAL_PREFIX)

# Path parameters
METRIC_PATH_PARAM = "/{metric}"
SUBMETRIC_PATH_PARAM = "/{submetric}"
DISPLAY_PATH_PARAM = "/{display}"
TERMINAL_PATH = f"{METRIC_PATH_PARAM}{SUBMETRIC_PATH_PARAM}{DISPLAY_PATH_PARAM}"


@router.get(TERMINAL_PATH)
async def terminal_path_op(
    metric: Metric,
    submetric: str,
    display: str,
    analysis: Annotated[list[str], Query()],
    view: Annotated[list[str], Query()],
    symbol: Annotated[list[str], Query()],
    request: Request,
):
    query_params: QueryParams = request.query_params

    async with AsyncClient(follow_redirects=True) as client:
        indiv_frames: list[LazyFrame] = await gather(
            *(
                METRIC_GEN[metric](client, sym, submetric, query_params)
                for sym in symbol
            )
        )

    merged_frames: LazyFrame = concat(
        indiv_frames, how="vertical_relaxed", parallel=True
    )
    print(merged_frames.collect())

    return {
        "metric": metric,
        "display": display,
        "analysis": analysis,
        "view": view,
        "symbol": symbol,
    }
