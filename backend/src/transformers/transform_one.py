from collections.abc import Callable

from polars import col, Expr, LazyFrame

from . import ColumnIdentifier

"""Transformations that apply to a single column"""


def percentage_change(
    data: LazyFrame, column: str, alias: str | None = None, n: int = 1
) -> LazyFrame:
    """
    The entry n rows behind is taken as the base: (xt - xt-n) / xt-n.

    The first n rows are null (nothing to compare against).
    Assumes the frame is in the correct order.

    args:
        alias: Default to overwriting column if not passed, otherwise write the
               results to a new column of name alias.
    """

    target: str = alias if alias is not None else column
    return data.with_columns(col(column).pct_change(n).alias(target))


def window_computation(
    data: LazyFrame,
    function: Callable[..., Expr],
    column: str,
    alias: str | None = None,
    window_size: int = 1,
    *args,
    **kwargs,
) -> LazyFrame:
    """Apply any Polars window operation over a fixed-size window.

    args:
        function: an unbound Expr rolling method, e.g. Expr.rolling_std or
        Expr.rolling_mean, which must have window_size as a parameter.
    """

    target: str = alias if alias is not None else column

    return data.with_columns(
        function(col(column), window_size=window_size, *args, **kwargs).alias(target)
    )


def scalar_product(
    data: LazyFrame, columns: ColumnIdentifier, scalar: int | float | Expr
) -> LazyFrame:
    """Multiply one or more columns by a constant, overwriting them in place."""

    return data.with_columns(col(columns) * scalar)
