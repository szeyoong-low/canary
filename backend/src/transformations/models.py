from datetime import date

from ..validators.primitives import ParamBaseModel, PositiveInt


class WindowFunction(ParamBaseModel):
    window: PositiveInt


class TimeHorizon(ParamBaseModel):
    horizon: PositiveInt


class DateIndex(ParamBaseModel):
    base: PositiveInt
    reference: date
