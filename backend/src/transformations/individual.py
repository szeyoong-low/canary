from collections.abc import Awaitable
from functools import partial, reduce
from math import sqrt

from httpx import AsyncClient
from polars import Expr, LazyFrame, col

from ..global_constants import DATE_KEY, TRANSFORMATION_SEPARATOR
from ..global_types import Column, Columns, Params
from ..validators.primitives import DateIndex, TimeHorizon, WindowFunction
from . import models
from .exceptions import AnalysisError
from .steps import _apply_unary_function

"""Compute values for a single entity"""

# Column names
BASE_METRIC: Column = ""
VOLATILITY: Column = "volatility"
RETURNS: Column = "returns"
INDEX_TO_DATE: Column = "index-to-date"


async def base_metric(
    data: Awaitable[LazyFrame],
    keys: Columns,
    depends: Column | None,
    params: Params,
    http_client: AsyncClient,
) -> LazyFrame:
    # Placeholder
    return await data


async def volatility(
    data: Awaitable[LazyFrame],
    keys: Columns,
    depends: Column | None,
    params: Params,
    http_client: AsyncClient,
) -> LazyFrame:
    """
    Calculate the volatility of a metric (usually returns on a financial
    instrument over time).

    Volatility is the standard deviation of observations multiplied by the
    square root of the number of observations in a rolling window.

    Source: https://www.investopedia.com/terms/v/volatility.asp#toc-how-to-calculate-volatility

    args:
        - depends: cannot be None
        - keys, http_client: unused but required to accept as part of contract
    """

    if depends is None:
        raise AnalysisError(f"{VOLATILITY} must be applied to a metric")

    window: int = WindowFunction.model_validate(params).window
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
    params: Params,
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
        raise AnalysisError(f"{RETURNS} must be applied to a metric")

    horizon: int = TimeHorizon.model_validate(params).horizon
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
    params: Params,
    http_client: AsyncClient,
) -> LazyFrame:
    """
    Create an index based on `reference`, which is assigned a value of `base`.

    args:
        - depends: cannot be None
        - http_client: unused but required to accept as part of contract
    """

    if depends is None:
        raise AnalysisError(f"{RETURNS} must be applied to a metric")

    if DATE_KEY not in keys:
        raise AnalysisError(f"{DATE_KEY} must be a key")

    model: DateIndex = DateIndex.model_validate(params)

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


type IndividualTransformation = (
    models.VolatilityModel | models.IndexToDateModel | models.ReturnsModel
)
