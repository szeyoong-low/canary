from typing import Callable, Literal

from fastapi import HTTPException
from httpx import codes
from polars import LazyFrame
from starlette.datastructures import QueryParams

from ..global_constants import DATE_KEY
from ..global_types import Column, Columns, Entities
from .input_models import HierarchyInputModel
from .output_models import Axis, ChartConfigModel
from .serialise import _serialise_cartesian, _serialise_hierarchy
from .style import _style_lines


type DisplayFunctionName = Literal["time-series", "treemap"]

"""
Contract of display functions for Cartesian charts

Input:
    - data (LazyFrame): Wide frame whose every column should be displayed.
    - keys (Columns)
    - entities (Entities)

Output: EChartsModel with all fields populated
"""

type DisplayCartesian = Callable[[LazyFrame, Columns, Entities], ChartConfigModel]

TIME_SERIES_ALLOWED_KEYS: Columns = {
    DATE_KEY,
}


def time_series(data: LazyFrame, keys: Columns, entities: Entities) -> ChartConfigModel:

    chart_config: ChartConfigModel = _serialise_cartesian(data)

    key_list: list[Column] = list(keys)
    if len(keys) != 1 or key_list[0] not in TIME_SERIES_ALLOWED_KEYS:
        raise HTTPException(
            codes.UNPROCESSABLE_ENTITY, "The data cannot be displayed as a time series"
        )

    chart_config.xAxis = [Axis(type="time")]
    chart_config.yAxis = [Axis(type="value")]

    data_cols: list[Column] = data.schema.names()
    key: Column = key_list.pop()
    data_cols.remove(key)

    return _style_lines(chart_config, data_cols, entities, key)


DISPLAY_CARTESIAN: dict[DisplayFunctionName, DisplayCartesian] = {
    "time-series": time_series,
}

"""
Contract of display functions for Hierarchical charts

Input:
    - data (LazyFrame): Wide frame whose every column should be displayed on hover.
    - drilldown (list[Column]): Columns used to create hierarchy, where the
        highest level is the first element and the lowest is the last.
        The lowest drilldown is to be used as labels
    - query_params (Starlette QueryParams), used to extract
        - aggregate_col (Column): Numeric column used for deaggregation and to
            determine the size of the displayed node
        - colour_col (ColumnOptional): Numeric column used to determine the
            colour based on a colour mapping. If None, Hue and tint are decided
            by top 2 levels.

Output: EChartsModel with all fields populated
"""

type DisplayHierarchy = Callable[
    [LazyFrame, list[Column], QueryParams], ChartConfigModel
]


def treemap(
    data: LazyFrame,
    drilldown: list[Column],
    query_params: QueryParams,
) -> ChartConfigModel:
    validated_input: HierarchyInputModel = HierarchyInputModel.model_validate(
        query_params
    )

    chart: ChartConfigModel = _serialise_hierarchy(
        data, drilldown, validated_input.aggregate_col
    )

    chart.series[0].type = "treemap"

    return chart


DISPLAY_HIERARCHY: dict[DisplayFunctionName, DisplayHierarchy] = {
    "treemap": treemap,
}
