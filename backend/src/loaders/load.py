from fastapi import HTTPException
from httpx import AsyncClient, codes, HTTPStatusError, Response
from polars import LazyFrame

from .constants import BASE_URL, ExternalAPI, ExternalEndpoint, NORMALISER
from ..types import Params


async def load_data(
    http_client: AsyncClient,
    external_api: ExternalAPI,
    endpoint: ExternalEndpoint,
    query_params: Params,
    headers: Params,
) -> LazyFrame:
    """
    Use the provided HTTP client to fetch data from the specified external API
    endpoint with the provided query parameters and HTTP headers.
    Load it into a LazyFrame and normalise into a wide shape.

    Args:
        http_client: HTTP client that supports concurrency
        external_api: external API identifier
        endpoint: external API endpoint path (must not have leading slash)
        query_params: key-value mapping to use as query parameters
        headers: key-value mapping to use in the request header

    Having the HTTP client supplied by the caller allows a connection pool to be
    shared, which eliminates redundant connection opening/closing and TLS handshakes.
    Source: https://www.python-httpx.org/advanced/clients/

    Returns:
        LazyFrame with data normalised.

    Raises:
        HTTPException 502: API returns a non-success status code, or API is not
            supported in the dispatch table
    """

    try:
        resource_url: str = f"{BASE_URL[external_api]()}{endpoint}"
    except KeyError:
        raise HTTPException(
            codes.INTERNAL_SERVER_ERROR,
            f"No base URL associated with the endpoint {external_api} in the dispatch table",
        )

    response: Response = await http_client.get(
        url=resource_url, params=query_params, headers=headers
    )

    try:
        response.raise_for_status()
    except HTTPStatusError:
        raise HTTPException(
            status_code=codes.INTERNAL_SERVER_ERROR,
            detail=(
                f"Error for at {response.url}:\n"
                f"HTTP {response.status_code}: {response.text}\n"
                f"Parameters: {query_params}\n"
                f"Headers: {headers}",
            ),
        )

    # Use the Polars lazy API to allow for optimisations
    try:
        return NORMALISER[external_api](LazyFrame(response.json()))
    except KeyError:
        raise HTTPException(
            codes.INTERNAL_SERVER_ERROR,
            f"No normalisation function associated with the endpoint {external_api} in the dispatch table",
        )
