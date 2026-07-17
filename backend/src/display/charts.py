from typing import Callable, Literal

from fastapi import HTTPException
from httpx import codes
from polars import DataFrame

from ..global_constants import DATE_KEY
from ..global_types import Column, Columns, Entities
from .models import Axis, ChartConfigModel
from .serialise import _serialise_cartesian
from .style import _style_lines


type DisplayFunctionName = Literal["time-series"]

"""
Contract of display functions for Cartesian charts

Input:
    - data (DataFrame): Wide frame whose every column should be displayed.
    - keys (Columns)
    - entities (Entities)

Output: EChartsModel with all fields populated
"""

type DisplayCartesian = Callable[[DataFrame, Columns, Entities], ChartConfigModel]

TIME_SERIES_ALLOWED_KEYS: Columns = {
    DATE_KEY,
}


def time_series(data: DataFrame, keys: Columns, entities: Entities) -> ChartConfigModel:

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
