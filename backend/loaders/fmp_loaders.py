from datetime import date

import httpx
from fastapi import HTTPException

from ..constants import fmp_constants, httpx_constants
from ..dependencies import dependency


async def fin_stmt(
    httpx_client: httpx.AsyncClient,
    endpoint: str,
    symbol: fmp_constants.Symbol,
    start: date,
    end: date,
    earnings_period: fmp_constants.EarningsPeriod,
) -> httpx.Response:
    """Fetch one financial statement from FMP for a single ticker.

    Raises HTTPException 502 if FMP returns a non-200 status.
    """
    env = dependency.get_environment()

    url = f"{env.fmp_base_url}{endpoint}"

    response = await httpx_client.get(
        url,
        params={
            fmp_constants.SYMBOL_PARAM: symbol,
            fmp_constants.LIMIT_PARAM: min(
                fmp_constants.MAX_FINANCIAL_STATEMENTS,
                end.year - start.year + 1,
            ),
            fmp_constants.PERIOD_PARAM: earnings_period,
            fmp_constants.APIKEY_PARAM: env.fmp_api_key,
        },
    )

    if response.status_code not in httpx_constants.VALID_STATUS_CODE:
        raise HTTPException(
            status_code=httpx.codes.INTERNAL_SERVER_ERROR,
            detail=f"FMP error for {symbol} at {endpoint}: HTTP {response.status_code}: {response.text}",
        )

    return response
