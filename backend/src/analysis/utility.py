from collections.abc import Awaitable, Collection, Iterable
from functools import reduce
from graphlib import CycleError, TopologicalSorter

from httpx import AsyncClient
from polars import LazyFrame, col
from polars import all as pl_all

from ..analysis.models import UNION_DISCRIMINATOR, Scope
from ..global_constants import ENTITY_TAG_SEPARATOR
from ..global_types import Columns, ImplementationError, Params
from .dispatch import ANALYSIS_FUNCTION_DISPATCH
from .exceptions import AnalysisError
from .models import (
    AggregateFunction,
    AnalysisFunction,
    BaseMetric,
    LinearFunction,
    ScopeMapping,
)


def _get_dependencies(
    node: AnalysisFunction,
    all_nodes: Collection[AnalysisFunction],
) -> Iterable[AnalysisFunction]:
    """
    Args:
        node: a single analysis function
        all_nodes: all analysis functions passed by the user

    Returns: those in `all_nodes` that `node` depends on

    Throws: AnalysisError
        - Predecessor references are invalid
        - Column names are not unique
    """

    predecessor_nodes: set[AnalysisFunction] = set()

    dependency_name: str
    for dependency_name in node.dependencies():
        matches: Iterable[AnalysisFunction] = filter(
            lambda x: x.name == dependency_name, all_nodes
        )

        if (match := next(matches, None)) is None:
            raise AnalysisError(
                f"{dependency_name} refers to an unknown column. Must be one of {[t.name for t in all_nodes]}"
            )

        if next(matches, None) is not None:
            raise AnalysisError(f"{dependency_name} is a duplicated column name")

        predecessor_nodes.add(match)

    return predecessor_nodes


def _resolve_column_scope(
    resolved_scopes: ScopeMapping,
    analysis_function: AnalysisFunction,
) -> ScopeMapping:
    """
    Checks that all dependencies of `analysis_function` are of the correct `Scope`.

    Args:
        - resolved_scopes: The resolved scopes (Scope.INDIVIDUAL or Scope.COLLECTIVE)
            of all analysis functions that come before `analysis_function` in the
            topological sort
        - analysis_function: The current analysis function checked

    Returns:
        Mapping updated with the analysis function's output column's `Scope`.

    Throws:
        - AnalysisError: a dependency resolved to the wrong `Scope`
        - ImplementationError:
            - A non-BaseMetric expects a dependency of Scope.BASE
            - An unknown AnalysisFunction type is encountered
    """

    updated_resolved_scopes: dict[str, Scope] = dict(resolved_scopes)
    output_scope: Scope

    if isinstance(analysis_function, BaseMetric):
        # Dependencies already checked
        output_scope = Scope.INDIVIDUAL
    else:
        # Invariant: only maps to Scope.INDIVIDUAL or Scope.COLLECTIVE
        dependency_scopes: ScopeMapping = analysis_function.dependencies()

        dependency: str
        required_scope: Scope
        for dependency, required_scope in dependency_scopes.items():
            match required_scope:
                case Scope.COLLECTIVE | Scope.INDIVIDUAL:
                    if required_scope != resolved_scopes[dependency]:
                        raise AnalysisError(
                            f"{analysis_function} expects {dependency} to be {required_scope}, but received {resolved_scopes[dependency]}"
                        )
                case Scope.BASE:
                    raise ImplementationError(
                        500,
                        f"Only base metrics can have a dependency of Scope.BASE, but {analysis_function} is a {type(analysis_function)}",
                    )
                case Scope.ANY:
                    pass  # No validation needed by definition

        if isinstance(analysis_function, AggregateFunction):
            output_scope = Scope.COLLECTIVE
        elif isinstance(analysis_function, LinearFunction):
            if all(v is Scope.COLLECTIVE for v in dependency_scopes.values()):
                output_scope = Scope.COLLECTIVE
            else:
                output_scope = Scope.INDIVIDUAL
        else:
            raise ImplementationError(
                500,
                "Only allow BaseMetric, AggregateFunction, or LinearFunction",
            )

    updated_resolved_scopes[analysis_function.name] = output_scope
    return updated_resolved_scopes


def validate_and_sort_analysis_functions(
    analysis_functions: Collection[AnalysisFunction],
    base_metrics: Columns,
) -> Iterable[AnalysisFunction]:
    """
    Args:
        analysis_functions: passed by the user
        base_metrics: columns in raw data

    Returns: Topological sort of `analysis_functions` based on dependency structure

    Throws: AnalysisError
        - Column names are not unique
        - Base metrics referenced are invalid
        - References to non-existent columns
        - No columns are displayed (and by extension, no analysis functions were specified)
        - Reference graph has cycles
    """

    dependency_adjacency_list: dict[AnalysisFunction, Iterable[AnalysisFunction]] = {}
    all_hidden: bool = True

    for node in analysis_functions:
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
            dependency_adjacency_list[node] = _get_dependencies(
                node, analysis_functions
            )

        if node.show:
            all_hidden = False

    if all_hidden:
        raise AnalysisError("At least one column must be shown.")

    try:
        sorted_analysis_functions: Iterable[AnalysisFunction] = [
            *TopologicalSorter(dependency_adjacency_list).static_order()
        ]
    except CycleError as e:
        raise AnalysisError(f"Cyclic references are not permitted: {e!s}")

    # Return value discarded, just for resolving and checking column scopes
    reduce(
        _resolve_column_scope,
        sorted_analysis_functions,
        {},
    )

    return sorted_analysis_functions


async def apply_analysis_function(
    data: Awaitable[LazyFrame],
    function: AnalysisFunction,
    keys: Columns,
    shared_params: Params,
    http_client: AsyncClient,
) -> LazyFrame:
    try:
        return await ANALYSIS_FUNCTION_DISPATCH[getattr(function, UNION_DISCRIMINATOR)](
            data, function, keys, shared_params, http_client
        )
    except KeyError:
        raise ImplementationError(
            500, f"{type(function)} must have a {UNION_DISCRIMINATOR} attribute"
        )


async def pivot_single_entity(
    data: Awaitable[LazyFrame], symbol: str, keys: Columns
) -> LazyFrame:
    return (await data).select(
        col(keys), pl_all().exclude(keys).name.prefix(symbol + ENTITY_TAG_SEPARATOR)
    )
