from collections.abc import Callable, Iterable
from typing import Concatenate, ParamSpec

from polars import LazyFrame


P = ParamSpec("P")

type ColumnIdentifier = str | Iterable[str]


"""Contract of the pipeline's transformation stages."""


"""Functions that take a LazyFrame (optimised DataFrame) and arbitrary arguments
and returns a LazyFrame"""
type Transform[**P] = Callable[Concatenate[LazyFrame, P], LazyFrame]
