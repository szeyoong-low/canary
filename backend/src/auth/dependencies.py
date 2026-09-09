from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from httpx import codes

from ..db.repositories.models import User
from ..db.repositories.platform_roles import (
    DEFAULT_PLATFORM_ROLE,
    grant_first_platform_role,
)
from ..db.repositories.users import get_active_user_by_subject, provision_user
from ..db.session import Session
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


# Written when the identity provider gave us neither a name nor an email. Users
# will be able to rename themselves, so a constant is enough.
FALLBACK_DISPLAY_NAME = "New user"


async def get_current_user(caller: Caller, session: Session) -> User:
    """
    Map the authenticated subject onto the local user row, creating it if this
    is the first time we have seen this subject.

    Just-in-time provisioning. Auth0 owns the user table and we only ever learn
    of a user by them turning up with a valid token, so there is no sign-up hook
    to write the row. The first authenticated request does it, and hands the new
    account its opening platform role.
    """

    user: User | None = await get_active_user_by_subject(session, caller.subject)

    if user is not None:
        return user

    user = await provision_user(
        session,
        caller.subject,
        caller.name or caller.email or FALLBACK_DISPLAY_NAME,
    )

    await grant_first_platform_role(session, user.user_id, DEFAULT_PLATFORM_ROLE)

    return user


# Note this opens a transaction that stays open for as long as the handler runs.
# Only routes that touch the database should depend on it. Long-lived ones (the
# agent) should keep depending on `authenticate` alone rather than pinning a
# pooled connection for the length of a stream. The frontend gates this anyways.
CurrentUser = Annotated[User, Depends(get_current_user)]
