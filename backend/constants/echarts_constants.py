from typing import Literal

type TooltipTrigger = Literal["item", "axis", "none"]

type AxisType = Literal["value", "category", "time", "log"]

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
