from typing import Any

from fastapi import HTTPException
from httpx import AsyncClient, codes
import polars as pl

from . import constants


async def load_dataframe(
    http_client: AsyncClient,
    api_base_url: str,
    endpoint: str,
    query_params: dict[str, Any],
) -> pl.DataFrame:
    """
    Use the provided HTTP client to fetch data from the specified external API
    endpoint with the provided query parameters.
    Load it into a dataframe with preliminary "tidying".

    Args:
        http_client: HTTP client that supports concurrency
        api_base_url: external API domain name (must have trailing slash)
        endpoint: external API endpoint path (must not have leading slash)
        query_params: any key-value mapping to use in the request

    Having the HTTP client supplied by the caller allows a connection pool to be
    shared, which eliminates redundant connection opening/closing and TLS handshakes.
    Source: https://www.python-httpx.org/advanced/clients/

    Returns:
        Dataframe with all nested fields unpivoted.

    Raises:
        HTTPException 502: API returns a non-success status code
    """

    resource_url = f"{api_base_url}{endpoint}"

    response = await http_client.get(url=resource_url, params=query_params)

    if response.status_code not in constants.SUCCESS_STATUS_CODES:
        raise HTTPException(
            status_code=codes.INTERNAL_SERVER_ERROR,
            detail=f"Error for {query_params} at {resource_url}: HTTP {response.status_code}: {response.text}",
        )

    df = pl.DataFrame(response.json())

    struct_cols, index_cols = set(), list()
    for cname, dtype in df.schema.items():
        if isinstance(dtype, pl.Struct):
            struct_cols.add(cname)
        else:
            index_cols.append(cname)

    # Use the Polars lazy API to allow for optimisations
    lf = df.lazy()

    for s in struct_cols:
        # Promotes all keys in the struct column to a top-level column
        lf = lf.unnest(s)

        # Spread the unnested columns over rows instead of columns by
        # melting them into a pair of key-value columns
        lf = lf.unpivot(
            index=index_cols,
            variable_name=constants.KEY_COLUMN_NAME,
            value_name=constants.VALUE_COLUMN_NAME,
        )

    if struct_cols:
        # Remove null rows created during unnesting
        lf = lf.filter(~pl.col(constants.VALUE_COLUMN_NAME).is_null())

    return lf.collect()
