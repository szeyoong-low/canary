from polars import col, LazyFrame, Struct

from . import constants


def _normalise_fmp(data: LazyFrame) -> LazyFrame:
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

        # Spread the unnested columns over rows instead of columns by
        # melting them into a pair of key-value columns
        data_normalised: LazyFrame = data_normalised.unpivot(
            index=index_cols,
            variable_name=constants.KEY_COLUMN_NAME,
            value_name=constants.VALUE_COLUMN_NAME,
        )

    if struct_cols:
        # Remove null rows created during unnesting
        return data_normalised.filter(~col(constants.VALUE_COLUMN_NAME).is_null())

    return data_normalised
