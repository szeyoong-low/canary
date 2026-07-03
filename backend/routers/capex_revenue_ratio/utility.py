from datetime import date

import httpx
import polars as pl

from ...constants import fmp_constants
from ...transformers.fmp import transform
from ...loaders import fmp_loaders


async def fetch_parse_fin_stmt(
    httpx_client: httpx.AsyncClient,
    endpoint: str,
    symbol: fmp_constants.Symbol,
    earnings_period: fmp_constants.EarningsPeriod,
    start: date,
    end: date,
    metric: str,
) -> pl.DataFrame:
    response = await fmp_loaders.fin_stmt(
        httpx_client, endpoint, symbol, start, end, earnings_period
    )

    return transform.fin_stmt_single_pct(
        response,
        symbol,
        start,
        end,
        fmp_constants.FISCAL_YEAR,
        metric,
    )
