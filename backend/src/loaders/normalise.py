from polars import LazyFrame, Struct


"""Normalise into a wide data shape, as explained in
https://github.com/szeyoong-low/canary/wiki/Wide-data-shape-as-default"""


def _normalise_fmp(data: LazyFrame) -> LazyFrame:

    struct_cols: set[str] = {
        cname
        for cname, dtype in data.collect_schema().items()
        if isinstance(dtype, Struct)
    }

    data_normalised: LazyFrame = data
    for s in struct_cols:
        # Promote all keys in the struct column to a top-level column
        data_normalised: LazyFrame = data_normalised.unnest(s)

    return data_normalised
