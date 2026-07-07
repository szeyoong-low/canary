from polars import LazyFrame

from . import ColumnIdentifier

"""Transformations that apply to multiple columns"""


def sort_data(data: LazyFrame, by: ColumnIdentifier, *arg, **kwarg) -> LazyFrame:
    """
    Wrapper for Polar's sort method on frames.
    This as a lazy query step, so it may be optimised by being pushed down.
    """

    return data.sort(by=by, *arg, **kwarg)
