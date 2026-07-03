from datetime import date
from typing import Annotated
from typing_extensions import Self

from pydantic import BaseModel, Field, model_validator

from ..constants import echarts_constants, fmp_constants
from ..validators import validators

Symbols = list[fmp_constants.Symbol]


class TimeSeriesBenchmark(BaseModel):
    tickers: Annotated[Symbols, Field(min_length=1)]
    start: date
    end: date
    period: fmp_constants.EarningsPeriod
    display: echarts_constants.SeriesType
    title: str = ""

    @model_validator(mode="after")
    def start_before_end(self) -> Self:
        validators.validate_date_range(self.start, self.end)
        return self
