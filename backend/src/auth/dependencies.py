from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from httpx import codes

from .token import AccessToken, decode

"""Where a bearer token becomes a caller FastAPI can hand to a route."""

# If `auto_error=True`, this scheme answers a missing or malformed header with
# `403 Forbidden`, which is reserved for authorisation errors. It also omits
# `WWW-Authenticate`, the header that tells a client how to authenticate.
# Turned off, the scheme returns None and the handling below answers with 401.
#
# Declaring the scheme at all is what puts the "Authorize" button in /docs and
# marks the protected routes in the OpenAPI schema.
bearer_scheme = HTTPBearer(auto_error=False)

AUTHENTICATE_HEADER = "WWW-Authenticate"


def _unauthorised(detail: str, *, token_supplied: bool) -> HTTPException:
    """
    A 401 shaped the way RFC 6750 asks for (https://www.rfc-editor.org/rfc/rfc6750#section-3)
    Error messages should be uninformative, otherwise attackers can probe defences.
    """

    return HTTPException(
        codes.UNAUTHORIZED,
        detail=detail,
        headers={
            AUTHENTICATE_HEADER: 'Bearer error="invalid_token"'
            if token_supplied
            else "Bearer"
        },
    )


async def authenticate(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> AccessToken:
    if credentials is None:
        raise _unauthorised("Not authenticated", token_supplied=False)

    try:
        return decode(credentials.credentials)
    except jwt.InvalidTokenError:
        raise _unauthorised("Invalid or expired token", token_supplied=True)


# Routes declare this so the annotation reads as `caller: Caller`.
Caller = Annotated[AccessToken, Depends(authenticate)]
