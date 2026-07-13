from datetime import date
from typing_extensions import Self

from pydantic import BaseModel, ConfigDict, model_validator

from .field import PositiveInt

"""Modular Pydantic models to be composed or used as-is for validating simple query parameters"""


class QueryBaseModel(BaseModel):
    model_config = ConfigDict(
        # Query parameters will be passed around functions implementing transformations.
        # Each will extract and validate the fields they need independently.
        extra="ignore",
    )


class DateRangeModel(QueryBaseModel):
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def _start_before_end(self) -> Self:
        if self.start_date > self.end_date:
            raise ValueError(
                f"Start date of {self.start_date} must be on or before end date of {self.end_date}"
            )

        return self


class WindowFunctionModel(QueryBaseModel):
    window: PositiveInt


class TimeHorizonModel(QueryBaseModel):
    horizon: PositiveInt


class DateIndexModel(QueryBaseModel):
    base: PositiveInt
    reference: date
