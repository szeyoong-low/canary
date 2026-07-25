from typing import Awaitable

from httpx import AsyncClient
from polars import LazyFrame, mean_horizontal

from .constants import TransformationDispatch
from .exceptions import AnalysisError
from ..global_constants import TRANSFORMATION_SEPARATOR
from ..global_types import Column, Columns, Params
from .steps import _apply_unary_function

"""Compute values for all entities"""

# Column names
GROUP_MEAN = "group-mean"


async def group_mean(
    data: Awaitable[LazyFrame],
    keys: Columns,
    depends: Column | None,
    params: Params,
    http_client: AsyncClient,
) -> LazyFrame:
    """
    Calculate the average of `depends` over all individual entities.

    args:
        - depends: cannot be None
        - keys, params, http_client: unused but required to accept as part of contract
    """

    if depends is None:
        raise AnalysisError(f"{GROUP_MEAN} must be applied to a metric")

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
