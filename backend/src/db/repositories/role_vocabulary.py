from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

"""Roles and their precedence"""

# Must keep in sync with seed.__main__.py
PLATFORM_ROLE_TABLE = "platform_role"
REPORT_ROLE_TABLE = "report_role"

# Cached as these tables are seeded and then only ever changed by a
# migration, both of which happen with the application stopped.
#
# Not `functools.cache`, which cannot wrap a coroutine. Two requests racing to
# fill an entry both read the same rows and write the same dict, so the race is
# wasteful at worst.
_precedence_by_role: dict[str, dict[str, int]] = {}


async def _get_precedence_by_role(session: AsyncSession, table: str) -> dict[str, int]:
    """Every role in one vocabulary and its rank, highest number outranking the rest."""

    if table not in _precedence_by_role:
        # A table name cannot be a bind parameter, so it is interpolated. Safe
        # only because `table` is one of the constants above and never reaches
        # here from a request.
        _precedence_by_role[table] = {
            role: precedence
            for role, precedence in (
                await session.execute(text(f"SELECT role, precedence FROM {table}"))
            ).all()
        }

    return _precedence_by_role[table]


class UnknownRoleError(Exception):
    """A role name that is not in the vocabulary. Always a programming error"""


async def get_precedence(session: AsyncSession, table: str, role: str) -> int:
    """The rank of one role. Raises `UnknownRoleError` if there is no such role."""

    precedence: int | None = (await _get_precedence_by_role(session, table)).get(role)

    if precedence is None:
        raise UnknownRoleError(f"No role named {role!r} in {table}")

    return precedence
