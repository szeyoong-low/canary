from collections.abc import Awaitable, Collection, Container, Iterable
from graphlib import CycleError, TopologicalSorter

from httpx import AsyncClient
from polars import LazyFrame, all, col

from ..global_constants import (
    EMPTY_STRING,
    TRANSFORMATION_SEPARATOR,
)
from ..global_types import Columns, Params
from .aggregate import AGGREGATE_TRANSFORMATIONS
from .exceptions import AnalysisError
from .individual import INDIVIDUAL_TRANSFORMATIONS
from .models import BaseMetric, Transformation


def _get_dependencies(
    node: Transformation,
    transformations: Collection[Transformation],
) -> Iterable[Transformation]:
    """
    Args:
        node: a single transformation
        transformations: all transformation passed by the user

    Returns: those in `transformations` that `node` depends on

    Throws: AnalysisError
        - Predecessor references are invalid
        - Column names are not unique
    """

    predecessor_nodes: set[Transformation] = set()

    for dependency_name in node.dependencies():
        matches: Iterable[Transformation] = filter(
            lambda x: x.name == dependency_name, transformations
        )

        if (match := next(matches, None)) is None:
            raise AnalysisError(
                f"{dependency_name} refers to an unknown column. Must be one of {transformations}"
            )

        if next(matches, None) is not None:
            raise AnalysisError(f"{dependency_name} is a duplicated column name")

        predecessor_nodes.add(match)

    return predecessor_nodes


def validate_and_sort_transformations(
    transformations: Collection[Transformation],
    base_metrics: Columns,
) -> Iterable[Transformation]:
    """
    Args:
        transformations: passed by the user
        base_metrics: columns in raw data

    Returns: Topological sort of `transformations` based on dependency structure

    Throws: AnalysisError
        - Column names are not unique
        - Base metrics are invalid
        - Predecessor references are invalid
        - No columns are displayed (and by extension, no analysis functions were specified)
        - Reference graph has cycles
    """

    dependency_adjacency_list: dict[Transformation, Iterable[Transformation]] = {}
    all_hidden: bool = True

    for node in transformations:
        if node in dependency_adjacency_list:
            raise AnalysisError(f"{node} is a duplicated column name")

        # Need to add base metrics to the list as they may not be included
        # implicitly through reference by other nodes
        dependency_adjacency_list[node] = set()

        if isinstance(node, BaseMetric):
            if node.metric not in base_metrics:
                raise AnalysisError(
                    f"{node} is not a base metric (one of {base_metrics})"
                )
        else:
            dependency_adjacency_list[node] = _get_dependencies(node, transformations)

        if node.show:
            all_hidden = False

    if all_hidden:
        raise AnalysisError("At least one column must be shown.")

    try:
        return [*TopologicalSorter(dependency_adjacency_list).static_order()]
    except CycleError as e:
        raise AnalysisError(f"Cyclic references are not permitted: {e!s}")


async def apply_analysis_function(
    data: Awaitable[LazyFrame],
    analysis: str,
    keys: Columns,
    params: Params,
    http_client: AsyncClient,
) -> LazyFrame:

    depends: str
    transformation: str
    depends, _, transformation = analysis.rpartition(TRANSFORMATION_SEPARATOR)

    try:
        # This is a constant time hashmap lookup, so we don't need to burden the
        # caller with specifying whether a transformation is individual or
        # aggregate.
        return await INDIVIDUAL_TRANSFORMATIONS[transformation](
            data, keys, depends, params, http_client
        )
    except KeyError:
        if transformation == EMPTY_STRING:
            # Must be an individual transformation with no dependencies
            try:
                return await INDIVIDUAL_TRANSFORMATIONS[depends](
                    data, keys, None, params, http_client
                )
            except KeyError:
                # Aggregate transformations must be applied on another metric
                raise AnalysisError(
                    f"Only individual transformations may have no dependencies {transformation}",
                )
        else:
            try:
                # Must be a aggregate transformation
                return await AGGREGATE_TRANSFORMATIONS[transformation](
                    data, keys, depends, params, http_client
                )
            except KeyError:
                raise AnalysisError(
                    f"Only individual transformations may have no dependencies {transformation}",
                )


async def pivot_single_entity(
    data: Awaitable[LazyFrame], symbol: str, keys: Columns
) -> LazyFrame:
    return (await data).select(
        col(keys), all().exclude(keys).name.prefix(symbol + TRANSFORMATION_SEPARATOR)
    )
