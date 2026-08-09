from collections.abc import Callable

from polars import Expr, LazyFrame, col

from ..global_constants import column_selection_regex
from ..global_types import Column, ColumnOptional

"""
Contract of a single step:

Inputs:
    - data (LazyFrame)
    - dest_col (Column | None): Hold the results of the desired computation.
        If None, it is left to the step function.

Output: Extension of input LazyFrame with all pre-existing columns unmodified.
"""


def _apply_unary_function(
    data: LazyFrame,
    source_col: Column,
    dest_col: ColumnOptional,
    function: Callable[[Expr], Expr],
) -> LazyFrame:
    """
    Apply a linear function or base metric aliasing. Same number of
    output columns as number of input columns.

    args:
        source_col: Target column(s). May be tagged (e.g. `AAPL/foo`) or
            untagged (e.g. `foo`).
        dest_col: Write the results to a new column of name `dest_col`, overwrite
            `source_col` if None, keeping the corresponding original tag.
        function: A unary function on a Polars expression implementing a linear
            function

    Precondition: All dependencies are present (guaranteed by topological sorting)
    """

    dest_col_name: Column = dest_col if dest_col is not None else source_col

    return data.with_columns(
        function(col(column_selection_regex(source_col, "any"))).name.map(
            lambda source_col_name: (
                source_col_name.removesuffix(source_col) + dest_col_name
            )
        )
    )


def _apply_unary_aggregation(
    data: LazyFrame,
    source_col: Column,
    dest_col: Column,
    function: Callable[[Expr], Expr],
) -> LazyFrame:
    """
    Apply an aggregate function. Exactly one output column.

    args:
        source_col: Target column(s). Must be tagged (e.g. `AAPL/foo`).
        dest_col: Write the results to a new column of name `dest_col`.
        function: A unary function on a Polars expression implementing an
            aggregate function.
    """

    return data.with_columns(
        function(col(column_selection_regex(source_col, "tagged"))).alias(dest_col)
    )
