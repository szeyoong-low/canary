from collections.abc import Awaitable
from functools import partial, reduce
from math import sqrt

from httpx import AsyncClient
from polars import Expr, LazyFrame, col

from ..global_constants import DATE_KEY
from ..global_types import Column, Columns, Params
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
    transformation: models.BaseMetric,
    keys: Columns,
    shared_params: Params,
    http_client: AsyncClient,
) -> LazyFrame:
    return _apply_unary_function(
        await data,
        transformation.metric,
        transformation.name,
        lambda x: x,
    )


async def volatility(
    data: Awaitable[LazyFrame],
    transformation: models.VolatilityModel,
    keys: Columns,
    shared_params: Params,
    http_client: AsyncClient,
) -> LazyFrame:
    return reduce(
        lambda lf, step: lf.pipe(step),
        [
            partial(
                _apply_unary_function,
                source_col=transformation.metric,
                dest_col=transformation.name,
                function=(
                    lambda x: Expr.rolling_std(x, window_size=transformation.window)
                ),
            ),
            partial(
                _apply_unary_function,
                source_col=transformation.name,
                dest_col=transformation.name,
                function=(lambda x: x * sqrt(transformation.window)),
            ),
        ],
        await data,
    )


async def returns(
    data: Awaitable[LazyFrame],
    transformation: models.ReturnsModel,
    keys: Columns,
    shared_params: Params,
    http_client: AsyncClient,
) -> LazyFrame:
    return reduce(
        lambda lf, step: lf.pipe(step),
        [
            partial(
                _apply_unary_function,
                source_col=transformation.metric,
                dest_col=transformation.name,
                function=(lambda x: Expr.pct_change(x, n=transformation.horizon)),
            ),
            partial(
                _apply_unary_function,
                source_col=transformation.name,
                dest_col=transformation.name,
                function=(lambda x: x * 100),
            ),
        ],
        await data,
    )


async def index_to_date(
    data: Awaitable[LazyFrame],
    transformation: models.IndexToDateModel,
    keys: Columns,
    shared_params: Params,
    http_client: AsyncClient,
) -> LazyFrame:

    if DATE_KEY not in keys:
        raise AnalysisError(f"{DATE_KEY} must be a key")

    return _apply_unary_function(
        data=await data,
        source_col=transformation.metric,
        dest_col=transformation.name,
        function=(
            lambda x: (
                (x / x.filter(col(DATE_KEY) == transformation.reference).first())
                * transformation.base
            )
        ),
    )


type AnyLinearFunction = (
    models.VolatilityModel | models.IndexToDateModel | models.ReturnsModel
)
