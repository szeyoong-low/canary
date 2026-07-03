import httpx
import polars as pl


def load_polars(
    response: httpx.Response,
    schema: dict[str, type],
) -> pl.DataFrame:

    data = response.json()

    # FMP returns an empty list when no data exists for the given period.
    if not data or not isinstance(data, list):
        return pl.DataFrame(schema=schema)

    return pl.DataFrame(data)
