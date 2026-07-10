from typing import Annotated

from asyncio import gather
from fastapi import APIRouter, Query, Request
from httpx import AsyncClient
from polars import concat, LazyFrame
from starlette.datastructures import QueryParams

from ...transformations import Metric, MetricGen, MetricGenParams
from ...transformations.metric_gen import METRIC_GEN


TERMINAL_PREFIX = "/terminal"
router = APIRouter(prefix=TERMINAL_PREFIX)

# Path parameters
METRIC_PATH_PARAM = "/{metric}"
SUBMETRIC_PATH_PARAM = "/{submetric}"
DISPLAY_PATH_PARAM = "/{display}"
TERMINAL_PATH = f"{METRIC_PATH_PARAM}{SUBMETRIC_PATH_PARAM}{DISPLAY_PATH_PARAM}"


@router.get(TERMINAL_PATH)
async def terminal_handler(
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
        metric_gen_params: MetricGenParams = METRIC_GEN[metric]
        metric_gen_fun: MetricGen = metric_gen_params["function"]

        indiv_frames: list[LazyFrame] = await gather(
            *(metric_gen_fun(client, sym, submetric, query_params) for sym in symbol)
        )

    merged_frames: LazyFrame = concat(indiv_frames, how="align_left", parallel=True)
    print(merged_frames.collect())

    return {
        "metric": metric,
        "display": display,
        "analysis": analysis,
        "view": view,
        "symbol": symbol,
    }
