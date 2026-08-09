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
    analysis_function: models.BaseMetric,
    keys: Columns,
    shared_params: Params,
    http_client: AsyncClient,
) -> LazyFrame:
    return _apply_unary_function(
        await data,
        analysis_function.metric,
        analysis_function.name,
        lambda x: x,
    )


async def volatility(
    data: Awaitable[LazyFrame],
    analysis_function: models.VolatilityModel,
    keys: Columns,
    shared_params: Params,
    http_client: AsyncClient,
) -> LazyFrame:
    return reduce(
        lambda lf, step: lf.pipe(step),
        [
            partial(
                _apply_unary_function,
                source_col=analysis_function.metric,
                dest_col=analysis_function.name,
                function=(
                    lambda x: Expr.rolling_std(x, window_size=analysis_function.window)
                ),
            ),
            partial(
                _apply_unary_function,
                source_col=analysis_function.name,
                dest_col=analysis_function.name,
                function=(lambda x: x * sqrt(analysis_function.window)),
            ),
        ],
        await data,
    )


async def returns(
    data: Awaitable[LazyFrame],
    analysis_function: models.ReturnsModel,
    keys: Columns,
    shared_params: Params,
    http_client: AsyncClient,
) -> LazyFrame:
    return reduce(
        lambda lf, step: lf.pipe(step),
        [
            partial(
                _apply_unary_function,
                source_col=analysis_function.metric,
                dest_col=analysis_function.name,
                function=(lambda x: Expr.pct_change(x, n=analysis_function.horizon)),
            ),
            partial(
                _apply_unary_function,
                source_col=analysis_function.name,
                dest_col=analysis_function.name,
                function=(lambda x: x * 100),
            ),
        ],
        await data,
    )


async def index_to_date(
    data: Awaitable[LazyFrame],
    analysis_function: models.IndexToDateModel,
    keys: Columns,
    shared_params: Params,
    http_client: AsyncClient,
) -> LazyFrame:

    if DATE_KEY not in keys:
        raise AnalysisError(f"{DATE_KEY} must be a key")

    return _apply_unary_function(
        data=await data,
        source_col=analysis_function.metric,
        dest_col=analysis_function.name,
        function=(
            lambda x: (
                (x / x.filter(col(DATE_KEY) == analysis_function.reference).first())
                * analysis_function.base
            )
        ),
    )


type AnyLinearFunction = (
    models.VolatilityModel | models.IndexToDateModel | models.ReturnsModel
)
