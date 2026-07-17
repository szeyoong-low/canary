from datetime import date

from ..validators.primitives import PositiveInt, QueryBaseModel


class WindowFunction(QueryBaseModel):
    window: PositiveInt


class TimeHorizon(QueryBaseModel):
    horizon: PositiveInt


class DateIndex(QueryBaseModel):
    base: PositiveInt
    reference: date
