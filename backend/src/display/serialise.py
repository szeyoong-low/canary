from polars import LazyFrame

from .models import ChartConfigModel, Dataset

"""Initialise a chart config model with a dataset"""


def _serialise_cartesian(data: LazyFrame) -> ChartConfigModel:
    return ChartConfigModel(
        dataset=[Dataset(source=data.collect().to_dict(as_series=False))]
    )
