from typing import Any

from fastapi import HTTPException
from httpx import AsyncClient, codes
import polars as pl

from . import constants
from .normalise import _normalise_fmp


async def load_data(
    http_client: AsyncClient,
    api_base_url: str,
    endpoint: str,
    query_params: dict[str, Any],
) -> pl.LazyFrame:
    """
    Use the provided HTTP client to fetch data from the specified external API
    endpoint with the provided query parameters.
    Load it into a LazyFrame with preliminary normalisation. Currently, only wide
    shape is supported.

    Args:
        http_client: HTTP client that supports concurrency
        api_base_url: external API domain name (must have trailing slash)
        endpoint: external API endpoint path (must not have leading slash)
        query_params: any key-value mapping to use in the request

    Having the HTTP client supplied by the caller allows a connection pool to be
    shared, which eliminates redundant connection opening/closing and TLS handshakes.
    Source: https://www.python-httpx.org/advanced/clients/

    Returns:
        LazyFrame with all nested fields unpivoted.

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

    # Use the Polars lazy API to allow for optimisations
    return _normalise_fmp(pl.LazyFrame(response.json()))
