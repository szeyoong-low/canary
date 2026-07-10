from polars import LazyFrame

from .models import ChartConfigModel, Dataset

"""
Initialise a chart config model with the following fields:
- title
- dataset
"""


def serialise_cartesian(data: LazyFrame) -> ChartConfigModel:
    return ChartConfigModel(dataset=[Dataset(source=[data.collect().to_dicts()])])
