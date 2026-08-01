from datetime import date

from ..validators.primitives import ParamBaseModel, PositiveInt


class WindowFunction(ParamBaseModel):
    """Required if these analysis functions are applied: volatility"""

    window: PositiveInt
    """Sliding window used for calculations (e.g. the last 20 entries are used
    to calculate a simple moving average)"""


class TimeHorizon(ParamBaseModel):
    """Required if these analysis functions are applied: returns"""

    horizon: PositiveInt
    """How many units of time define a period of analysis (e.g. returns over a
    month/20 trading days). This can be inferred implicitly, e.g. daily returns
    means horizon=1"""


class DateIndex(ParamBaseModel):
    """Required if these analysis functions are applied: index_to_date"""

    base: PositiveInt = 100
    """The quantity that represents the indexed metric on the reference date"""

    reference: date
    """The date when the index metric is given the value `base`. Whenever
    possible, this should be a trading day. For example, if the user says
    "from the first day", make sure `reference` is the first trading day."""
