from typing import Generic, TypeVar

from pydantic import BaseModel

from ..constants import echarts_constants

TL = TypeVar("TL")
TX = TypeVar("TX")
TS = TypeVar("TS")


class EChartsModel(BaseModel):
    model_config = {"extra": "forbid"}


class Title(EChartsModel):
    text: str = ""


class Tooltip(EChartsModel):
    trigger: echarts_constants.TooltipTrigger = "item"


class Legend(EChartsModel, Generic[TL]):
    data: list[TL]


class XAxis(EChartsModel, Generic[TX]):
    type: echarts_constants.AxisType
    data: list[TX]


class YAxis(EChartsModel):
    type: echarts_constants.AxisType


class Series(EChartsModel, Generic[TS]):
    name: str
    type: echarts_constants.SeriesType
    data: list[TS]


class ChartConfig(EChartsModel, Generic[TL, TX, TS]):
    title: Title
    tooltip: Tooltip
    legend: Legend[TL]
    xAxis: XAxis[TX]
    yAxis: YAxis
    series: list[Series[TS]]
