from typing import Callable, Literal

from fastapi import HTTPException
from httpx import codes
from polars import LazyFrame

from ..global_constants import DATE_KEY
from ..global_types import Column, Columns, ColumnOptional, Entities
from .output_models import Axis, ChartConfigModel
from .serialise import _serialise_series, _serialise_hierarchy
from .style import _style_lines


type DisplayFunctionName = Literal["time-series", "treemap"]

"""
Contract of display functions for Series charts

Input:
    - data (LazyFrame): Wide frame whose every column should be displayed.
    - keys (Columns)
    - entities (Entities)

Output: EChartsModel with all fields populated
"""

type DisplaySeries = Callable[[LazyFrame, Columns, Entities], ChartConfigModel]

TIME_SERIES_ALLOWED_KEYS: Columns = {
    DATE_KEY,
}


def time_series(data: LazyFrame, keys: Columns, entities: Entities) -> ChartConfigModel:

    chart_config: ChartConfigModel = _serialise_series(data)

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


DISPLAY_SERIES: dict[DisplayFunctionName, DisplaySeries] = {
    "time-series": time_series,
}

"""
Contract of display functions for Hierarchical charts

Input:
    - data (LazyFrame): Wide frame whose every column should be displayed on
        hover. Should have been drilled down and aggregated, so there should be
        only one row for each entity at the lowest drilldown.
    - drilldown (list[Column]): Columns used to create hierarchy, where the
        highest level is the first element and the lowest is the last.
        The lowest drilldown is to be used as labels
    - aggregate_col (Column): Numeric column used for deaggregation and to
        determine the size of the displayed node
    - colour_col (ColumnOptional): Numeric column used to determine the
        colour based on a colour mapping. If None, Hue and tint are decided
        by top 2 levels.

Output: EChartsModel with all fields populated
"""

type DisplayHierarchy = Callable[
    [LazyFrame, list[Column], Column, ColumnOptional], ChartConfigModel
]


def treemap(
    data: LazyFrame,
    drilldown: list[Column],
    aggregate_col: Column,
    colour_col: ColumnOptional,
) -> ChartConfigModel:

    chart: ChartConfigModel = _serialise_hierarchy(
        data, drilldown, aggregate_col, colour_col
    )

    chart.series[0].type = "treemap"

    return chart


DISPLAY_HIERARCHY: dict[DisplayFunctionName, DisplayHierarchy] = {
    "treemap": treemap,
}
