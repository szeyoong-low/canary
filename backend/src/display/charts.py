from polars import DataFrame
from typing import Callable

from .models import ChartConfigModel
from .serialise import _serialise_cartesian
from ..types import Columns

"""
Contract of display functions

Input:
    - data (DataFrame): Wide frame whose every column should be displayed.
    - keys (Columns)

Output: EChartsModel with the following fields populated
    - `dataset`
    - `series`
    - `legend`

"""

type DisplayFunction = Callable[[DataFrame, Columns], ChartConfigModel]


def time_series(data: DataFrame, keys: Columns) -> ChartConfigModel:
    serialised: ChartConfigModel = _serialise_cartesian(data)
    return serialised


DISPLAY_FUNCTIONS: dict[str, DisplayFunction] = {
    "time-series": time_series,
}
