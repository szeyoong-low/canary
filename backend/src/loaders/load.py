from typing import Any

from fastapi import HTTPException
from httpx import AsyncClient, codes, Response
from polars import LazyFrame

from . import constants


async def load_data(
    http_client: AsyncClient,
    external_api: constants.ExternalAPI,
    endpoint: str,
    query_params: dict[str, Any],
    headers: dict[str, Any],
) -> LazyFrame:
    """
    Use the provided HTTP client to fetch data from the specified external API
    endpoint with the provided query parameters.
    Load it into a LazyFrame with preliminary normalisation. Currently, only wide
    shape is supported.

    Args:
        http_client: HTTP client that supports concurrency
        api_base_url: external API domain name (must have trailing slash)
        endpoint: external API endpoint path (must not have leading slash)
        query_params: key-value mapping to use as query parameters
        headers: key-value mapping to use in the request header

    Having the HTTP client supplied by the caller allows a connection pool to be
    shared, which eliminates redundant connection opening/closing and TLS handshakes.
    Source: https://www.python-httpx.org/advanced/clients/

    Returns:
        LazyFrame with all nested fields unpivoted.

    Raises:
        HTTPException 502: API returns a non-success status code
    """

    try:
        resource_url: str = f"{constants.BASE_URL[external_api]()}{endpoint}"
    except KeyError:
        raise HTTPException(
            codes.INTERNAL_SERVER_ERROR,
            "No base URL associated with the endpoint in the dispatch table.",
        )

    response: Response = await http_client.get(
        url=resource_url, params=query_params, headers=headers
    )

    if response.status_code not in constants.SUCCESS_STATUS_CODES:
        raise HTTPException(
            status_code=codes.INTERNAL_SERVER_ERROR,
            detail=(
                f"Error for at {resource_url}:\n"
                f"HTTP {response.status_code}: {response.text}\n"
                f"Parameters: {query_params}\n"
                f"Headers: {headers}",
            ),
        )

    # Use the Polars lazy API to allow for optimisations
    return constants.NORMALISER[external_api](LazyFrame(response.json()))
