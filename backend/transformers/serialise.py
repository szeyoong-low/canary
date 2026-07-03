import polars as pl

from ..constants import echarts_constants
from ..models import echarts


def time_series_benchmark(
    dataframe: pl.DataFrame,
    series_type: echarts_constants.SeriesType,
    index: str,
    chart_title: str,
) -> echarts.ChartConfig[str, str, float | None]:
    title = echarts.Title(text=chart_title)
    tooltip = echarts.Tooltip()
    legend = echarts.Legend(data=dataframe.columns)

    xAxis = echarts.XAxis(
        type="category", data=dataframe.select(index).to_series().to_list()
    )

    yAxis = echarts.YAxis(type="value")

    series = [
        echarts.Series(name=col.name, type=series_type, data=col.to_list())
        for col in dataframe
        if col.name != index
    ]

    return echarts.ChartConfig(
        title=title,
        tooltip=tooltip,
        legend=legend,
        xAxis=xAxis,
        yAxis=yAxis,
        series=series,
    )
