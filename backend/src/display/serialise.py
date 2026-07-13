from polars import DataFrame

from .models import ChartConfigModel, Dataset

"""Initialise a chart config model with a dataset"""


def _serialise_cartesian(data: DataFrame) -> ChartConfigModel:
    return ChartConfigModel(dataset=[Dataset(source=[data.to_dict(as_series=False)])])
