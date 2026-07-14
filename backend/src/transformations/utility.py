from collections.abc import Container, Iterable
from typing import Awaitable

from fastapi import HTTPException
from httpx import AsyncClient, codes
from polars import all, col, LazyFrame
from starlette.datastructures import QueryParams

from .collective import COLLECTIVE_TRANSFORMATIONS
from ..global_constants import (
    EMPTY_STRING,
    INITIAL_METRIC_SEPARATOR,
    TRANSFORMATION_SEPARATOR,
)
from ..global_types import Columns
from .individual import INDIVIDUAL_TRANSFORMATIONS


def resolve_transformations(
    analysis_list: Iterable[str], base_metrics: Container[str]
) -> tuple[Iterable[str], Iterable[str]]:
    """
    Generate a topological sort of individual transformations that are not no-ops
    and a set of collective transformations from a list of analysis functions.

    Args:
        - analysis: list of strings encoding analysis functions in the form
            `foo/bar/baz`, where `foo` and `foo/bar` are its dependencies
            and `baz` is the transformation to be composed on them
        - base_matrics: names of columns that must already be present and
            can be assumed as such by transformations

    Returns:
        - First: List of strings encoding individual transformations.
            These are fully resolved into their dependencies and ordered
            topologically with duplicates and base metrics removed.
            For example, `foo/bar/baz` (where `foo` is a base metric and `baz`
            is an individual transformation) will be resolved into `foo/bar`
            and `foo/bar/baz` (in this order). If `foo/bar` is encountered later,
            it will be ignored.
        - Second: Set of strings encoding collective transformations
            with duplicates removed

    Raises:
        - HTTPException 502: an analysis function is not well-formed
    """

    individual: set[str] = set()
    collective: set[str] = set()
    base_metric_count: int = 0

    for analysis in analysis_list:
        transformation_list: list[str] = analysis.split(TRANSFORMATION_SEPARATOR)

        # Build up by appending transformations
        composed_transformation: str = transformation_list[0]

        # Check first transformation
        # We allow a single base metrics or transformations, or a list of them
        # delimited with `+`
        first_transformations: list[str] = composed_transformation.split(
            INITIAL_METRIC_SEPARATOR
        )

        for metric in first_transformations:
            if metric in base_metrics:
                base_metric_count += 1  # No-op, must already in the frame
            elif metric in INDIVIDUAL_TRANSFORMATIONS:
                individual.add(metric)
            else:
                # Collective transformation or unrecognised specification
                raise HTTPException(
                    codes.UNPROCESSABLE_ENTITY,
                    f"{metric} must be a base metric or an individual transformation",
                )

        if len(transformation_list) > 1:
            # Check intermediate transformations
            for transformation in transformation_list[1:-1]:
                if transformation not in INDIVIDUAL_TRANSFORMATIONS:
                    raise HTTPException(
                        codes.UNPROCESSABLE_ENTITY,
                        f"{transformation} in {analysis} must be an individual transformation",
                    )

                composed_transformation += TRANSFORMATION_SEPARATOR + transformation
                individual.add(composed_transformation)

            last_transformation: str = transformation_list[-1]

            if last_transformation in INDIVIDUAL_TRANSFORMATIONS:
                individual.add(analysis)
            elif last_transformation in COLLECTIVE_TRANSFORMATIONS:
                collective.add(analysis)
            else:
                raise HTTPException(
                    codes.UNPROCESSABLE_ENTITY,
                    f"{last_transformation} in {analysis} must be a transformation",
                )

    if (len(individual) + len(collective) + base_metric_count) == 0:
        raise HTTPException(
            codes.UNPROCESSABLE_ENTITY,
            "Analysis functions must be specified using query parameters, e.g. analysis=foo/bar/baz",
        )

    # Sort by number of items composed, so that dependencies are always resolved.
    # Better to use a set to remove duplicates and sort at the end O(n logn),
    # than reject duplicates manually and insert into a sorted list O(n).
    # O(n) constant time hashset insertions + 1 O(n logn) quicksort vs
    # O(n * (logn + n)) binary search and insert (need to shift elements)
    # where n is the total number of transformations (e.g. `foo/bar/baz` has 3)
    return (
        sorted(individual, key=lambda s: s.count(TRANSFORMATION_SEPARATOR)),
        collective,
    )


async def apply_analysis_function(
    data: Awaitable[LazyFrame],
    analysis: str,
    keys: Columns,
    query_params: QueryParams,
    http_client: AsyncClient,
) -> LazyFrame:

    depends: str
    transformation: str
    depends, _, transformation = analysis.rpartition(TRANSFORMATION_SEPARATOR)

    try:
        # This is a constant time hashmap lookup, so we don't need to burden the
        # caller with specifying whether a transformation is individual or
        # collective.
        return await INDIVIDUAL_TRANSFORMATIONS[transformation](
            data, keys, depends, query_params, http_client
        )
    except KeyError:
        if transformation == EMPTY_STRING:
            # Must be an individual transformation with no dependencies
            try:
                return await INDIVIDUAL_TRANSFORMATIONS[depends](
                    data, keys, None, query_params, http_client
                )
            except KeyError:
                # Collective transformations must be applied on another metric
                raise HTTPException(
                    codes.UNPROCESSABLE_ENTITY,
                    f"Only individual transformations may have no dependencies {transformation}",
                )
        else:
            try:
                # Must be a collective transformation
                return await COLLECTIVE_TRANSFORMATIONS[transformation](
                    data, keys, depends, query_params, http_client
                )
            except KeyError:
                raise HTTPException(
                    codes.UNPROCESSABLE_ENTITY,
                    f"Only individual transformations may have no dependencies {transformation}",
                )


async def pivot_single_entity(
    data: Awaitable[LazyFrame], symbol: str, keys: Columns
) -> LazyFrame:
    return (await data).select(
        col(keys), all().name.prefix(symbol + TRANSFORMATION_SEPARATOR)
    )
