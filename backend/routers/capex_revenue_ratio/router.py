import asyncio
from typing import Annotated

from fastapi import APIRouter, Query
import httpx

from . import utility
from ...constants import fmp_constants
from ...models import echarts, query
from ...transformers import merge, serialise

ROUTER_PREFIX = "/capex-revenue-ratio"
TIME_SERIES_BENCHMARK_ENDPOINT = "/time-series-benchmark"


router = APIRouter(prefix=ROUTER_PREFIX)


@router.get(
    TIME_SERIES_BENCHMARK_ENDPOINT,
    response_model=echarts.ChartConfig[str, str, float | None],
)
async def time_series_benchmark(
    query: Annotated[query.TimeSeriesBenchmark, Query()],
) -> echarts.ChartConfig[str, str, float | None]:

    async with httpx.AsyncClient(follow_redirects=True) as client:
        individual_tickers = await asyncio.gather(
            *[
                utility.fetch_parse_fin_stmt(
                    client,
                    fmp_constants.KEY_METRICS,
                    ticker,
                    query.period,
                    query.start,
                    query.end,
                    fmp_constants.CAPEX_TO_REVENUE,
                )
                for ticker in query.tickers
            ]
        )

    years = list(map(str, range(query.start.year, query.end.year + 1)))

    merged = merge.individual_ticker_data(
        individual_tickers, years, fmp_constants.FISCAL_YEAR
    )

    return serialise.time_series_benchmark(
        merged, query.display, fmp_constants.FISCAL_YEAR, query.title
    )
