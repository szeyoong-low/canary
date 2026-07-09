from datetime import date
from typing_extensions import Self

from pydantic import BaseModel, ConfigDict, model_validator

"""Modular Pydantic models to be composed or used as-is for validating simple query parameters"""


COMMON_CONFIG: ConfigDict = ConfigDict(
    # Query parameters will be passed around amongst functions implementing transformations.
    # Each will extract and validate the fields they need independently.
    extra="ignore",
)


class DateRangeModel(BaseModel):
    model_config = COMMON_CONFIG

    start_date: date
    end_date: date

    @model_validator(mode="after")
    def start_before_end(self) -> Self:
        if self.start_date > self.end_date:
            raise ValueError(
                f"Start date of {self.start_date} must be on or before end date of {self.end_date}"
            )

        return self
