from collections.abc import Container
from datetime import date
from types import UnionType
from typing import Annotated, Any, Self, Union, get_args, get_origin

from pydantic import AfterValidator, BaseModel, ConfigDict, model_validator
from pydantic.fields import FieldInfo
from starlette.datastructures import QueryParams

from ..global_types import Params

"""Modular Pydantic models to be composed or used as-is for validating simple parameters"""


class ParamBaseModel(BaseModel):
    model_config = ConfigDict(
        # Parameters will be passed around functions implementing transformations.
        # Each will extract and validate the fields they need independently.
        extra="ignore",
        use_attribute_docstrings=True,
    )

    @staticmethod
    def _is_collection_type(annotation: Any) -> bool:
        """
        Whether a field annotation ultimately holds a collection of values.

        Unwraps unions (e.g. `set[str] | None`) so an optional collection still counts.
        """

        origin: Any = get_origin(annotation)

        if origin in (Union, UnionType):
            return any(
                ParamBaseModel._is_collection_type(arg) for arg in get_args(annotation)
            )

        return isinstance(origin, type) and issubclass(origin, Container)

    @classmethod
    def validate_query_params(cls, raw_params: QueryParams) -> Self:
        """
        Validate a Starlette `QueryParams` multidict into this model.

        A repeated key (`exchange=NASDAQ&exchange=NYSE`) in `QueryParams`
        carries several values, but Pydantic uses plain mapping access which
        keeps only one. We shape the raw values before running Pydantic.
        """

        shaped_params: Params = {}

        name: str
        field: FieldInfo
        for name, field in cls.model_fields.items():
            if name not in raw_params:
                continue

            if ParamBaseModel._is_collection_type(field.annotation):
                shaped_params[name] = raw_params.getlist(name)
            else:
                shaped_params[name] = raw_params[name]

        return cls.model_validate(shaped_params)


def _check_positive_int(n: int) -> int:
    if n > 0:
        return n

    raise ValueError(f"{n} must be a positive integer")


type PositiveInt = Annotated[int, AfterValidator(_check_positive_int)]


def _check_nonempty_string(s: str) -> str:
    if s.strip():
        return s

    raise ValueError(f"{s} cannot be empty")


type NonEmptyString = Annotated[str, AfterValidator(_check_nonempty_string)]


class DateRangeModel(ParamBaseModel):
    start_date: date
    """Must be on or before end_date"""

    end_date: date
    """Must be on or after start_date"""

    @model_validator(mode="after")
    def _start_before_end(self) -> Self:
        if self.start_date > self.end_date:
            raise ValueError(
                f"Start date of {self.start_date} must be on or before end date of {self.end_date}"
            )

        return self


class WindowFunction(ParamBaseModel):
    window: PositiveInt
    """Sliding window used for calculations (e.g. the last 20 entries are used
    to calculate a simple moving average)"""


class TimeHorizon(ParamBaseModel):
    horizon: PositiveInt
    """How many units of time define a period of analysis (e.g. returns over a
    month/20 trading days). This can be inferred implicitly, e.g. daily returns
    means horizon=1"""


class DateIndex(ParamBaseModel):
    base: PositiveInt = 100
    """The quantity that represents the indexed metric on the reference date"""

    reference: date
    """The date when the index metric is given the value `base`. Whenever
    possible, this should be a trading day. For example, if the user says
    "from the first day", make sure `reference` is the first trading day."""
