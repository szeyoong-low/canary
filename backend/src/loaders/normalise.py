from collections.abc import Iterable
from functools import reduce

from polars import col, LazyFrame, Struct

from ..global_constants import DATE_KEY


"""Normalise into a wide data shape, as explained in
https://github.com/szeyoong-low/canary/wiki/Wide-data-shape-as-default"""


def _normalise_fmp(data: LazyFrame) -> LazyFrame:

    struct_cols: Iterable[str] = {
        cname
        for cname, dtype in data.collect_schema().items()
        if isinstance(dtype, Struct)
    }

    # Promote all keys in the struct column to a top-level column
    data_normalised: LazyFrame = reduce(
        (lambda lf, s: lf.unnest(s)),
        struct_cols,
        data,
    )

    # Try parsing dates
    if DATE_KEY in data_normalised.collect_schema():
        return data_normalised.with_columns(col(DATE_KEY).str.to_date().alias(DATE_KEY))

    return data_normalised
