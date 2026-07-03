from typing import TypeVar

import polars as pl

T = TypeVar("T")


def individual_ticker_data(
    individual_dataframes: list[pl.DataFrame],
    index: list[T],
    index_name: str,
) -> pl.DataFrame:
    """Left-join DataFrames onto a scaffold to produce a pivoted DataFrame.

    Each frame must have columns [<index_name>, <ticker>].
    Rows with no data for a ticker become null.
    """
    scaffold = pl.DataFrame({index_name: index})

    for frame in individual_dataframes:
        scaffold = scaffold.join(frame, on=index_name, how="left")

    return scaffold
