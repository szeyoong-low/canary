from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

"""The report role vocabulary: the names, and what each one outranks."""

# Cached as the table is seeded and then only ever changed by a
# migration, both of which happen with the application stopped.
#
# Not `functools.cache`, which cannot wrap a coroutine. Two requests racing to
# fill this both read the same rows and write the same dict, so the race is
# wasteful at worst.
_precedence_by_role: dict[str, int] | None = None


async def _get_precedence_by_role(session: AsyncSession) -> dict[str, int]:
    """Every report role and its rank, highest number outranking the rest."""

    global _precedence_by_role

    if _precedence_by_role is None:
        _precedence_by_role = {
            role: precedence
            for role, precedence in (
                await session.execute(text("SELECT role, precedence FROM report_role"))
            ).all()
        }

    return _precedence_by_role


class UnknownRoleError(Exception):
    """A role name that is not in the vocabulary. Always a programming error"""


async def get_precedence(session: AsyncSession, role: str) -> int:
    """The rank of one role. Raises `UnknownRoleError` if there is no such role."""

    precedence: int | None = (await _get_precedence_by_role(session)).get(role)

    if precedence is None:
        raise UnknownRoleError(f"No report role named {role!r}")

    return precedence
