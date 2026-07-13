from typing import Literal

from pydantic import BaseModel, ConfigDict

from ..types import Params

# Will not use generic types to enforce that lists are homogeneous:
# 1. It doesn't matter for ECharts rendering
# 2. Since we nest models in lists, using a generic type means all of the list
#    elements will have the same type, which is often not the case in ECharts

# Using BaseModel instead of nested models can provide a 2.5x speedup.
# However, it doesn't allow me to set default values.
# https://pydantic.dev/docs/validation/latest/concepts/performance/#use-BaseModel-over-nested-models


class EChartsBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Title(EChartsBaseModel):
    text: str = ""


class Dataset(EChartsBaseModel):
    # Row-objects: to_dicts
    # Columnar: to_dict (preferred: no repeated key strings, easier CSV conversion)
    source: list[Params] | dict[str, list] = dict()


class Tooltip(EChartsBaseModel):
    trigger: Literal["item", "axis", "none"] = "item"


class Legend(EChartsBaseModel):
    data: list = list()


class Axis(EChartsBaseModel):
    type: Literal["value", "category", "time", "log"]
    data: list | None = None


type SeriesType = Literal[
    "line",
    "bar",
    "pie",
    "scatter",
    "effectScatter",
    "radar",
    "tree",
    "treemap",
    "sunburst",
    "boxplot",
    "candlestick",
    "heatmap",
    "map",
    "parallel",
    "lines",
    "graph",
    "sankey",
    "funnel",
    "gauge",
    "pictorialBar",
    "themeRiver",
    "chord",
    "custom",
]


class Series(EChartsBaseModel):
    name: str = ""
    type: SeriesType
    yAxisIndex: int = 0
    data: list | None = None


class ChartConfigModel(EChartsBaseModel):
    title: Title | None = None
    dataset: list[Dataset] | None = None
    tooltip: Tooltip = Tooltip()
    legend: Legend = Legend()
    xAxis: list[Axis] = list()
    yAxis: list[Axis] = list()
    series: list[Series] = list()
