from polars import LazyFrame, Struct


def _normalise_fmp(data: LazyFrame) -> LazyFrame:
    """Normalise into a wide data shape, as explained in
    https://github.com/szeyoong-low/canary/wiki/Load-flexibly-transform-deterministically
    """

    struct_cols: set[str] = set()
    index_cols: list[str] = list()
    for cname, dtype in data.collect_schema().items():
        if isinstance(dtype, Struct):
            struct_cols.add(cname)
        else:
            index_cols.append(cname)

    data_normalised: LazyFrame = data
    for s in struct_cols:
        # Promotes all keys in the struct column to a top-level column
        data_normalised: LazyFrame = data_normalised.unnest(s)

    return data_normalised
