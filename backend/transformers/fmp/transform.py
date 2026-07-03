from datetime import date

import httpx
import polars as pl

from . import load_polars
from ...constants import fmp_constants


def fin_stmt_single_pct(
    response: httpx.Response,
    symbol: fmp_constants.Symbol,
    start: date,
    end: date,
    index: str,
    metric: str,
) -> pl.DataFrame:
    return _fin_stmt(
        response,
        start,
        end,
        index,
        {str(symbol): pl.Float64},
        [(pl.col(metric) * 100).round(2).alias(str(symbol))],
    )


def _fin_stmt(
    response: httpx.Response,
    start: date,
    end: date,
    index: str,
    data_col_schema: dict[str, type],
    data_col_transforms: list[pl.Expr],
) -> pl.DataFrame:
    """Parse a FMP response containing a financial statement into a year-indexed
    DataFrame of one or more metrics for one ticker.

    Returns a DataFrame with columns [fiscalYear, <ticker>].
    Returns an empty DataFrame with the correct schema if FMP returns no data.
    """

    assert len(data_col_schema) == len(data_col_transforms)

    full_schema = {index: pl.String} | data_col_schema
    data = load_polars.load_polars(response, full_schema)

    return data.select(
        pl.col(index),
        *data_col_transforms,
    ).filter(
        pl.col(index).cast(pl.Int32) >= start.year,
        pl.col(index).cast(pl.Int32) <= end.year,
    )
