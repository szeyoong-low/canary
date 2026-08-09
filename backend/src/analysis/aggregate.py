from collections.abc import Awaitable

from httpx import AsyncClient
from polars import LazyFrame, mean_horizontal

from ..global_types import Column, Columns, Params
from . import models
from .steps import _apply_unary_aggregation

"""Compute values for all entities"""

# Column names
GROUP_MEAN: Column = "group-mean"


async def group_mean(
    data: Awaitable[LazyFrame],
    transformation: models.GroupMeanModel,
    keys: Columns,
    shared_params: Params,
    http_client: AsyncClient,
) -> LazyFrame:
    return _apply_unary_aggregation(
        data=await data,
        source_col=transformation.metric,
        dest_col=transformation.name,
        function=mean_horizontal,
    )


type AnyAggregateFunction = models.GroupMeanModel
