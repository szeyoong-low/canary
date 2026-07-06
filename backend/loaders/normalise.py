import polars as pl

from . import constants


def _normalise_fmp(data: pl.LazyFrame) -> pl.LazyFrame:
    struct_cols: set[str] = set()
    index_cols: list[str] = list()
    for cname, dtype in data.collect_schema().items():
        if isinstance(dtype, pl.Struct):
            struct_cols.add(cname)
        else:
            index_cols.append(cname)

    for s in struct_cols:
        # Promotes all keys in the struct column to a top-level column
        data = data.unnest(s)

        # Spread the unnested columns over rows instead of columns by
        # melting them into a pair of key-value columns
        data = data.unpivot(
            index=index_cols,
            variable_name=constants.KEY_COLUMN_NAME,
            value_name=constants.VALUE_COLUMN_NAME,
        )

    if struct_cols:
        # Remove null rows created during unnesting
        return data.filter(~pl.col(constants.VALUE_COLUMN_NAME).is_null())

    return data
