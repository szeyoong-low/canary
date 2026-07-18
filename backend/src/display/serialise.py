from polars import DataFrame, LazyFrame

from ..global_types import Column, ColumnOptional, Params
from .output_models import ChartConfigModel, Dataset, Series

"""Initialise a chart config model with a dataset"""


def _serialise_series(data: LazyFrame) -> ChartConfigModel:
    return ChartConfigModel(
        dataset=[Dataset(source=data.collect().to_dict(as_series=False))]
    )


HIERARCHY_NAME_FIELD: str = "name"
HIERARCHY_VALUE_FIELD: str = "value"
HIERARCHY_CHILDREN_FIELD: str = "children"


def _serialise_hierarchy(
    data: LazyFrame,
    drilldown: list[Column],
    aggregate_col: Column,
    colour_col: ColumnOptional = None,
) -> ChartConfigModel:

    return ChartConfigModel(
        series=[
            Series(
                type="treemap",  # Do not rely on this behaviour! Caller should set
                data=_build_nodes(data.collect(), drilldown, aggregate_col, colour_col),
            )
        ],
    )


def _build_nodes(
    data: DataFrame,
    drilldown: list[Column],
    aggregate_col: Column,
    colour_col: ColumnOptional,
) -> list[Params]:
    """Recursive depth-first construction of the hierarchy tree"""

    curr_level: Column
    next_levels: list[Column]
    curr_level, *next_levels = drilldown

    nodes: list[Params] = []

    # We cannot use lazy execution as a LazyGroupBy is not iterable. We would
    # have to collect the results. This re-executes the whole upstream query
    # plan, and results cannot be shared.
    entity: str
    subtree: DataFrame
    for (entity,), subtree in data.group_by(curr_level):
        if next_levels:  # Interior node
            nodes.append(
                {
                    HIERARCHY_NAME_FIELD: entity,
                    HIERARCHY_CHILDREN_FIELD: _build_nodes(
                        subtree, next_levels, aggregate_col, colour_col
                    ),
                }
            )
        else:
            nodes.append(_build_leaf(subtree, entity, aggregate_col, colour_col))

    return nodes


def _build_leaf(
    data: DataFrame, entity: str, aggregate_col: Column, colour_col: ColumnOptional
) -> Params:
    # Every column rides along as hover data (params.data.<col> in the tooltip).
    node: Params = data.row(0, named=True)
    node[HIERARCHY_NAME_FIELD] = entity
    node[HIERARCHY_VALUE_FIELD] = data[aggregate_col].sum()

    if colour_col is not None:
        # Overwrite in place so the summed colour stays consistent with value,
        # and a later style pass finds it under its own column name.
        node[colour_col] = data[colour_col].sum()

    return node
