from functools import partial
from math import sqrt

from polars import Expr, LazyFrame

from . import transform_collective as many
from . import transform_individual as one
from .utility import _fold_transforms

"""Computing values that only require data for a single entity"""


def volatility(
    data: LazyFrame,
    metric: str,
    period: int,
    window: int,
    sort_key: str,
    alias: str = "volatility",
) -> LazyFrame:
    """
    Calculate the volatility of a "metric" (usually a financial instrument)
    over time ("from" and "to" - precondition that the series is clipped to this).

    Volatility is the standard deviation of the percentage change over a fixed
    "period" multiplied by the square root of the number of periods in a rolling "window"

    Source: https://www.investopedia.com/terms/v/volatility.asp#toc-how-to-calculate-volatility
    """

    percentage_change_col = "percentage_change"

    return _fold_transforms(
        data,
        [
            partial(many.sort_data, by=sort_key),
            partial(
                one.percentage_change,
                column=metric,
                alias=percentage_change_col,
                n=period,
            ),
            partial(
                one.window_computation,
                function=Expr.rolling_std,
                column=percentage_change_col,
                alias=alias,
                window_size=window,
            ),
            partial(one.scalar_product, column=alias, scalar=sqrt(window)),
        ],
    )
