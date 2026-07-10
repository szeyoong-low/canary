from typing import Literal

from pydantic import BaseModel, ConfigDict

from ..utility.types import Params

# Will not use generic types to enforce that lists are homogeneous:
# 1. It doesn't matter for ECharts rendering
# 2. Since we nest models in lists, using a generic type means all of the list
#    elements will have the same type, which is often not the case in ECharts

# Using BaseModel instead of nested models can provide a 2.5x speedup.
# However, it doesn't allow me to set default values.
# https://pydantic.dev/docs/validation/latest/concepts/performance/#use-BaseModel-over-nested-models


STANDARD_CONFIG = ConfigDict(extra="forbid")


class EChartsModel(BaseModel):
    model_config = STANDARD_CONFIG


class Title(EChartsModel):
    text: str = ""


class Dataset(EChartsModel):
    source: list[Params] | list[list] = list()


class Tooltip(EChartsModel):
    trigger: Literal["item", "axis", "none"] = "item"


class Legend(EChartsModel):
    data: list = list()


class Axis(EChartsModel):
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


class Series(EChartsModel):
    name: str = ""
    type: SeriesType
    yAxisIndex: int = 0
    data: list | None = None


class ChartConfigModel(EChartsModel):
    title: Title | None = None
    dataset: list[Dataset] | None = None
    tooltip: Tooltip = Tooltip()
    legend: Legend = Legend()
    xAxis: list[Axis] = list()
    yAxis: list[Axis] = list()
    series: list[Series] = list()
