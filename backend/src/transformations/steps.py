from collections.abc import Callable

from polars import col, Expr, LazyFrame

from ..global_constants import individual_entity_regex
from ..global_types import Column, ColumnOptional

"""
Contract of a single step:

Inputs:
    - data (LazyFrame)
    - dest_col (str | None): column to hold the results of the desired
        computation. If None, it is left to the step function.

Output: Extension of input LazyFrame with all pre-existing columns unmodified.
"""


def _apply_unary_function(
    data: LazyFrame,
    source_col: Column,
    dest_col: ColumnOptional,
    function: Callable[[Expr], Expr],
    aggregate: bool = False,
) -> LazyFrame:
    """
    args:
        source_col: Target column
        dest_col: Write the results to a new column of name `dest_col`,
            overwrite `source_col` if None.
        function: Any unary function on a Polars expression
        aggregate: If this is a horizontal aggregate function, the source columns
            will be `source_col` of each individual entity
    """

    return data.with_columns(
        function(
            col(individual_entity_regex(source_col) if aggregate else source_col)
        ).alias(dest_col if dest_col is not None else source_col)
    )
