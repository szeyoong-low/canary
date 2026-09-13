from collections.abc import Awaitable, Callable
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from httpx import codes
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.repositories.models import PlatformRole, User
from ..db.repositories.platform_roles import (
    DEFAULT_PLATFORM_ROLE,
    get_current_platform_role,
    grant_first_platform_role,
)
from ..db.repositories.role_vocabulary import PLATFORM_ROLE_TABLE, get_precedence
from ..db.repositories.users import get_active_user_by_subject, provision_user
from ..db.session import DBSession
from ..global_constants import PlatformRoleName
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


def unauthorised(detail: str, *, token_supplied: bool) -> HTTPException:
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


async def authenticate_optionally(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> AccessToken | None:
    """
    Identify the caller if they offered a token, and let them through
    anonymously if they did not.

    Note the asymmetry: no token is a visitor, but a token that fails
    verification is still a 401. Degrading a rejected token to anonymous would
    show a signed-in user the logged-out view of their own report with nothing
    to tell them their session had expired.
    """

    if credentials is None:
        return None

    try:
        return decode(credentials.credentials)
    except jwt.InvalidTokenError:
        raise unauthorised("Invalid or expired token", token_supplied=True)


type OptionalCaller = Annotated[AccessToken | None, Depends(authenticate_optionally)]


async def authenticate(caller: OptionalCaller) -> AccessToken:
    """The same check, for routes where being anonymous is not allowed."""

    # FastAPI resolves each dependency once per request, so no duplicate work
    if caller is None:
        raise unauthorised("Not authenticated", token_supplied=False)

    return caller


# Routes declare this so the annotation reads as `caller: Caller`.
type Caller = Annotated[AccessToken, Depends(authenticate)]


# Written when the identity provider gave us neither a name nor an email. Users
# will be able to rename themselves, so a constant is enough.
FALLBACK_DISPLAY_NAME = "New user"


async def _resolve_user(session: AsyncSession, caller: AccessToken) -> User:
    """
    Map an authenticated subject onto the local user row, creating it if this is
    the first time we have seen this subject.

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


async def get_current_user(caller: Caller, session: DBSession) -> User:
    return await _resolve_user(session, caller)


# Note this opens a transaction that stays open for as long as the handler runs.
# Only routes that touch the database should depend on it. Long-lived ones (the
# agent) should keep depending on `authenticate` alone rather than pinning a
# pooled connection for the length of a stream. The frontend gates this anyways.
type CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_current_user_or_none(
    caller: OptionalCaller, session: DBSession
) -> User | None:
    """The local user row for whoever is calling, or `None` for a visitor."""
    return None if caller is None else await _resolve_user(session, caller)


type OptionalUser = Annotated[User | None, Depends(get_current_user_or_none)]


async def resolve_platform_role(
    user: OptionalUser, session: DBSession
) -> PlatformRole | None:
    """What the caller may do on the platform itself. `None` for a visitor who is
    not signed in."""
    return (
        None if user is None else await get_current_platform_role(session, user.user_id)
    )


type CallerPlatformRole = Annotated[PlatformRole | None, Depends(resolve_platform_role)]


def require_platform_role(
    minimum_role: PlatformRoleName,
) -> Callable[..., Awaitable[PlatformRole]]:
    """
    Build a dependency that lets a caller through only if they hold at least
    `minimum_role` on the platform, and returns that role so the route does not
    have to ask for it twice.

    A factory for the same reason as `reports.dependencies.require_report_role`:
    a FastAPI dependency takes only what injection can give it, so the one thing
    that varies per route has to be closed over.

    Used as:
        role: Annotated[PlatformRole, Depends(require_platform_role("admin"))]

    There is no equivalent of `reports.policy` here because platform standing
    has only one source. A caller either holds a role outranking the bar or they
    do not, so the rule is the comparison below and nothing more.
    """

    async def guard(role: CallerPlatformRole, session: DBSession) -> PlatformRole:
        if role is None:
            raise unauthorised("Not authenticated", token_supplied=False)

        if role.precedence < await get_precedence(
            session, PLATFORM_ROLE_TABLE, minimum_role
        ):
            raise HTTPException(
                codes.FORBIDDEN, f"Requires at least the {minimum_role} role"
            )

        return role

    return guard


# The lowest standing that still counts as a participant rather than a spectator.
ACTIVE_PLATFORM_ROLE: PlatformRoleName = DEFAULT_PLATFORM_ROLE


async def get_active_user_or_none(
    user: OptionalUser, role: CallerPlatformRole, session: DBSession
) -> User | None:
    """
    Whoever is calling, provided they are in good standing. `None` for a visitor
    who is not signed in, and equally for a suspended account (shown what a
    logged-out one is shown).

    For routes where being anonymous is an ordinary state to be in.
    """

    if user is None or role is None:
        return None

    if role.precedence < await get_precedence(
        session, PLATFORM_ROLE_TABLE, ACTIVE_PLATFORM_ROLE
    ):
        return None

    return user


type ActiveUser = Annotated[User | None, Depends(get_active_user_or_none)]
