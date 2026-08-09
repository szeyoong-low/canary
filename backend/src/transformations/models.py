from collections.abc import Mapping
from enum import Enum, auto
from functools import cache
from typing import Annotated, Literal

from ..validators import primitives as models


class Scope(Enum):
    """Describes whether a metric/column describes a single entity or is an
    aggregate over all entities. Used to annotate fields naming dependencies."""

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


type ScopeMapping = Mapping[str, Scope]


class Transformation(models.ParamBaseModel):
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

    @classmethod
    @cache
    def _dependency_fields(cls) -> ScopeMapping:
        """
        Returns: Every field that names another transformation. This is fixed
        when the class is defined so the reflection is cacheable.

        Precondition: Every field has at most one Scope tag.
        """

        return {
            field_name: meta
            for field_name, field_info in cls.model_fields.items()
            for meta in field_info.metadata
            if isinstance(meta, Scope)
        }

    # Not suitable for global caching with @functools.cache:
    # 1. https://docs.astral.sh/ruff/rules/cached-instance-method/
    # 2.__hash__ has been overridden, so column name will determine dependencies
    # even though this varies per instance
    def dependencies(self) -> ScopeMapping:
        """Returns: The name of each analysis function this one depends on."""

        dependencies: ScopeMapping = {}
        field_name: str
        scope: Scope
        for field_name, scope in self._dependency_fields().items():
            dependency: str | None = getattr(self, field_name)
            if dependency is not None:
                dependencies[dependency] = scope
        return dependencies


UNION_DISCRIMINATOR: str = "analysis"


class BaseMetric(Transformation):
    """A column from raw data (`metric`) renamed as `name`"""

    analysis: Literal[""]
    metric: Annotated[models.NonEmptyString, Scope.BASE]


class SingularTransformation(Transformation):
    pass


class VolatilityModel(SingularTransformation, models.WindowFunction):
    """
    Calculate volatility of a metric (usually returns on a financial instrument
    over time).

    Standard deviation of observations multiplied by the square root of the
    number of observations in a rolling window.
    """

    # Source: https://www.investopedia.com/terms/v/volatility.asp#toc-how-to-calculate-volatility

    analysis: Literal["volatility"]  # Must match Column name in individual.py

    metric: Annotated[models.NonEmptyString, Scope.ANY]


class ReturnsModel(SingularTransformation, models.TimeHorizon):
    """Calculate the percentage change of a metric over a given horizon (number
    of observations)."""

    analysis: Literal["returns"]  # Must match Column name in individual.py

    metric: Annotated[models.NonEmptyString, Scope.ANY]


class IndexToDateModel(SingularTransformation, models.DateIndex):
    """Create an index based on `reference`, which is assigned a value of `base`."""

    analysis: Literal["index-to-date"]  # Must match Column name in individual.py

    metric: Annotated[models.NonEmptyString, Scope.ANY]


class AggregateTransformation(Transformation):
    pass


class GroupMeanModel(AggregateTransformation):
    """Calculate the average of `depends` over all individual entities."""

    analysis: Literal["group-mean"]  # Must match Column name in aggregate.py

    metric: Annotated[models.NonEmptyString, Scope.INDIVIDUAL]
