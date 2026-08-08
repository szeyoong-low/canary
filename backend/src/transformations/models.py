from abc import ABC
from enum import Enum, auto
from typing import Annotated, Literal

from ..validators import primitives as models


class Transformation(ABC, models.ParamBaseModel):
    # Docstrings are hoisted into the system prompt as they are shared by every
    # analysis function's model.
    name: models.NonEmptyString
    show: bool = True

    def __eq__(self, value: object) -> bool:
        return isinstance(value, Transformation) and self.name.__eq__(value.name)

    def __hash__(self) -> int:
        return self.name.__hash__()

    def __str__(self) -> str:
        return self.name


class Scope(Enum):
    """Describes whether a metric/column describes a single entity or is an
    aggregate over all entities."""

    BASE = auto()
    """A base metric (column in raw data). Used to describe a column's
    dependencies but not itself (use INDIVIDUAL instead)."""

    INDIVIDUAL = auto()
    """Belongs to a single entity, e.g. revenue of AAPL."""

    AGGREGATE = auto()
    """Aggregate over multiple entities, e.g. mean revenue of the Magnificent Seven."""

    ANY = auto()
    """Both INDIVIDUAL and AGGREGATE are accepted, but will lead to different
    behaviour. Used to describe a column's dependencies but not itself (use
    INDIVIDUAL or AGGREGATE)."""


"""Used as metadata tags on fields of analysis functions that name dependencies."""

type RefBase = Annotated[models.NonEmptyString, Scope.BASE]
type RefIndividual = Annotated[models.NonEmptyString, Scope.INDIVIDUAL]
type RefAggregate = Annotated[models.NonEmptyString, Scope.AGGREGATE]
type RefAny = Annotated[models.NonEmptyString, Scope.ANY]


UNION_DISCRIMINATOR: str = "analysis"


class BaseMetric(Transformation):
    """A column from raw data (`metric`) renamed as `name`"""

    analysis: Literal[""]
    metric: RefBase


class VolatilityModel(Transformation, models.WindowFunction):
    """
    Calculate volatility of a metric (usually returns on a financial instrument
    over time).

    Standard deviation of observations multiplied by the square root of the
    number of observations in a rolling window.
    """

    # Source: https://www.investopedia.com/terms/v/volatility.asp#toc-how-to-calculate-volatility

    analysis: Literal["volatility"]  # Must match Column name in individual.py

    metric: RefAny


class ReturnsModel(Transformation, models.TimeHorizon):
    """Calculate the percentage change of a metric over a given horizon (number
    of observations)."""

    analysis: Literal["returns"]  # Must match Column name in individual.py

    metric: RefAny


class IndexToDateModel(Transformation, models.DateIndex):
    """Create an index based on `reference`, which is assigned a value of `base`."""

    analysis: Literal["index-to-date"]  # Must match Column name in individual.py

    metric: RefAny


class GroupMeanModel(Transformation):
    """Calculate the average of `depends` over all individual entities."""

    analysis: Literal["group-mean"]  # Must match Column name in aggregate.py

    metric: RefIndividual
