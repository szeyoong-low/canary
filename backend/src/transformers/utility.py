from collections.abc import Callable

from functools import reduce

from polars import LazyFrame


def fold_transforms(
    data: LazyFrame, transforms: list[Callable[[LazyFrame], LazyFrame]]
) -> LazyFrame:
    """Fold each transformation in the list (order matters) over the data,
    starting from the leftmost"""
    return reduce(lambda lf, step: lf.pipe(step), transforms, data)
