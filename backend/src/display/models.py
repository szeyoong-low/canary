from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, ConfigDict

from ..global_types import Params

# Will not use generic types to enforce that lists are homogeneous:
# 1. It doesn't matter for ECharts rendering
# 2. Since we nest models in lists, using a generic type means all of the list
#    elements will have the same type, which is often not the case in ECharts

# Using BaseModel instead of nested models can provide a 2.5x speedup.
# However, it doesn't allow me to set default values.
# https://pydantic.dev/docs/validation/latest/concepts/performance/#use-BaseModel-over-nested-models


MIN_RGB: int = 0
MAX_RGB: int = 255


def _validate_rgb(n: int) -> int:
    if MIN_RGB <= n <= MAX_RGB:
        return n

    raise ValueError(f"{n} must lie between {MIN_RGB} and {MAX_RGB} inclusive")


type ByteField = Annotated[int, AfterValidator(_validate_rgb)]

NORMALISED_FLOOR: float = 0
NORMALISED_CEILING: float = 1


def _validate_normalised_float(x: float) -> float:
    if NORMALISED_FLOOR <= x <= NORMALISED_CEILING:
        return x

    raise ValueError(
        f"{x} must lie between {NORMALISED_FLOOR} and {NORMALISED_CEILING} inclusive"
    )


type NormalisedFloatField = Annotated[float, AfterValidator(_validate_normalised_float)]

HEX_PREFIX: str = "#"


def _validate_hex_string(string: str) -> str:
    if (
        2 <= len(string) <= 7
        and string[0] == HEX_PREFIX
        and all((c.isalnum() for c in string[1:]))
    ):
        return string

    raise ValueError(f"{string} is not in the format #ABC123")


type HexColor = Annotated[str, AfterValidator(_validate_hex_string)]

type Number = int | float


def _validate_non_negative_number(n: Number) -> Number:
    if n > 0:
        return n

    raise ValueError(f"{n} must be a positive number")


type NonNegativeNumberField = Annotated[
    Number, AfterValidator(_validate_non_negative_number)
]


class EChartsBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class RGBA(EChartsBaseModel):
    red: ByteField = 0
    green: ByteField = 0
    blue: ByteField = 0
    alpha: NormalisedFloatField = 1


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


class LineStyle(EChartsBaseModel):
    color: RGBA | HexColor = "#000"
    width: NonNegativeNumberField = 2
    type: Literal["solid", "dashed", "dotted"] = "solid"
    dashOffset: NonNegativeNumberField = 0
    cap: Literal["butt", "round", "square"] = "butt"
    join: Literal["bevel", "round", "miter"] = "bevel"


class ItemStyle(EChartsBaseModel):
    color: RGBA | HexColor = "#000"


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
    encode: dict | None = None
    lineStyle: LineStyle = LineStyle()
    itemStyle: ItemStyle = ItemStyle()
    showSymbol: bool = True


class ChartConfigModel(EChartsBaseModel):
    title: Title = Title()
    dataset: list[Dataset]
    tooltip: Tooltip = Tooltip()
    legend: Legend = Legend()
    xAxis: list[Axis] = list()
    yAxis: list[Axis] = list()
    series: list[Series] = list()
