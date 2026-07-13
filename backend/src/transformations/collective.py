from typing import Awaitable

from fastapi import HTTPException
from httpx import AsyncClient, codes
from polars import LazyFrame, mean_horizontal
from starlette.datastructures import QueryParams

from .constants import TransformationDispatch
from ..constants import TRANSFORMATION_SEPARATOR
from .steps import _apply_unary_function
from ..types import Column, Columns

"""Compute values for all entities"""

# Column names
GROUP_MEAN = "group-mean"


async def group_mean(
    data: Awaitable[LazyFrame],
    keys: Columns,
    depends: Column | None,
    query_params: QueryParams,
    http_client: AsyncClient,
) -> LazyFrame:
    """
    Calculate the average of `depends` over all individual entities.

    args:
        - depends: cannot be None
        - keys, query_params, http_client: unused but required to accept as part of contract
    """

    if depends is None:
        raise HTTPException(
            codes.UNPROCESSABLE_ENTITY, f"{GROUP_MEAN} must be applied to a metric"
        )

    return _apply_unary_function(
        data=await data,
        source_col=depends,
        dest_col=depends + TRANSFORMATION_SEPARATOR + GROUP_MEAN,
        function=mean_horizontal,
        aggregate=True,
    )


# Invariant: Transformations must be registered in exactly one of
# INDIVIDUAL_TRANSFORMATIONS or COLLECTIVE_TRANSFORMATIONS
COLLECTIVE_TRANSFORMATIONS: TransformationDispatch = {
    GROUP_MEAN: group_mean,
}
