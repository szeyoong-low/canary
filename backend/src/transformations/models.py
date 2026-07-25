from datetime import date

from ..validators.primitives import PositiveInt, ParamBaseModel


class WindowFunction(ParamBaseModel):
    window: PositiveInt


class TimeHorizon(ParamBaseModel):
    horizon: PositiveInt


class DateIndex(ParamBaseModel):
    base: PositiveInt
    reference: date
