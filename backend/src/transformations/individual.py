from functools import partial, reduce
from math import sqrt
from typing import Awaitable

from fastapi import HTTPException
from httpx import AsyncClient, codes
from polars import col, Expr, LazyFrame
from starlette.datastructures import QueryParams

from . import models
from .constants import TransformationDispatch
from ..global_constants import DATE_KEY, TRANSFORMATION_SEPARATOR
from ..global_types import Column, Columns
from .steps import _apply_unary_function

"""Compute values for a single entity"""

# Column names
VOLATILITY = "volatility"
RETURNS = "returns"
INDEX_TO_DATE = "index-to-date"


async def volatility(
    data: Awaitable[LazyFrame],
    keys: Columns,
    depends: Column | None,
    query_params: QueryParams,
    http_client: AsyncClient,
) -> LazyFrame:
    """
    Calculate the volatility of a metric (usually returns on a financial
    instrument over time).

    Volatility is the standard deviation of observations multiplied by the
    square root of the number of observations in a rolling window

    Source: https://www.investopedia.com/terms/v/volatility.asp#toc-how-to-calculate-volatility

    args:
        - depends: cannot be None
        - keys, http_client: unused but required to accept as part of contract
    """

    if depends is None:
        raise HTTPException(
            codes.UNPROCESSABLE_ENTITY, f"{VOLATILITY} must be applied to a metric"
        )

    window: int = models.WindowFunction.model_validate(query_params).window
    dest_col: Column = depends + TRANSFORMATION_SEPARATOR + VOLATILITY

    return reduce(
        lambda lf, step: lf.pipe(step),
        [
            partial(
                _apply_unary_function,
                source_col=depends,
                dest_col=dest_col,
                function=(lambda x: Expr.rolling_std(x, window_size=window)),
            ),
            partial(
                _apply_unary_function,
                source_col=dest_col,
                dest_col=dest_col,
                function=(lambda x: x * sqrt(window)),
            ),
        ],
        await data,
    )


async def returns(
    data: Awaitable[LazyFrame],
    keys: Columns,
    depends: Column | None,
    query_params: QueryParams,
    http_client: AsyncClient,
) -> LazyFrame:
    """
    Calculate the percentage change of a metric over a given horizon
    (number of observations).

    args:
        - depends: cannot be None
        - keys, http_client: unused but required to accept as part of contract
    """

    if depends is None:
        raise HTTPException(
            codes.UNPROCESSABLE_ENTITY, f"{RETURNS} must be applied to a metric"
        )

    horizon: int = models.TimeHorizon.model_validate(query_params).horizon
    dest_col: Column = depends + TRANSFORMATION_SEPARATOR + RETURNS

    return reduce(
        lambda lf, step: lf.pipe(step),
        [
            partial(
                _apply_unary_function,
                source_col=depends,
                dest_col=dest_col,
                function=(lambda x: Expr.pct_change(x, n=horizon)),
            ),
            partial(
                _apply_unary_function,
                source_col=dest_col,
                dest_col=dest_col,
                function=(lambda x: x * 100),
            ),
        ],
        await data,
    )


async def index_to_date(
    data: Awaitable[LazyFrame],
    keys: Columns,
    depends: str | None,
    query_params: QueryParams,
    http_client: AsyncClient,
) -> LazyFrame:
    """
    Create an index based on `reference`, which is assigned a value of `base`.

    args:
        - depends: cannot be None
        - http_client: unused but required to accept as part of contract
    """

    if depends is None:
        raise HTTPException(
            codes.UNPROCESSABLE_ENTITY, f"{RETURNS} must be applied to a metric"
        )

    if DATE_KEY not in keys:
        raise HTTPException(codes.UNPROCESSABLE_ENTITY, f"{DATE_KEY} must be a key")

    model: models.DateIndex = models.DateIndex.model_validate(query_params)

    return _apply_unary_function(
        data=await data,
        source_col=depends,
        dest_col=depends + TRANSFORMATION_SEPARATOR + INDEX_TO_DATE,
        function=(
            lambda x: (
                (x / col(depends).filter(col(DATE_KEY) == model.reference).first())
                * model.base
            )
        ),
    )


# Invariant: Transformations must be registered in exactly one of
# INDIVIDUAL_TRANSFORMATIONS or COLLECTIVE_TRANSFORMATIONS
INDIVIDUAL_TRANSFORMATIONS: TransformationDispatch = {
    VOLATILITY: volatility,
    RETURNS: returns,
    INDEX_TO_DATE: index_to_date,
}
