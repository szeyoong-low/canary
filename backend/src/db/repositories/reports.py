from collections.abc import Sequence
from uuid import UUID

from fastapi import status
from sqlalchemy import Row, text
from sqlalchemy.ext.asyncio import AsyncSession

from ...global_types import ImplementationError
from .exceptions import NotFoundError
from .models import ReportHeader, ReportPreviewRecord
from .platform_roles import SYSTEM_SUBJECT
from .role_vocabulary import REPORT_ROLE_TABLE, get_precedence

"""Every query that touches `report` and its two ledgers."""

DEFAULT_REPORT_TITLE: str = "New report"

# Must keep in sync with seed.__main__.py
CREATOR_ROLE: str = "owner"

# ne statement rather than three keeps it to a single round trip.
#
# If that account is missing, `grantor` is empty, both child inserts write no
# rows, and the final SELECT returns nothing, which the caller turns into an error.
_CREATE_REPORT = """
    WITH grantor AS (
        SELECT user_id FROM app_user WHERE auth0_subject = :system_subject
    ),
    new_report AS (
        INSERT INTO report (title)
        VALUES (:title)
        RETURNING report_id
    ),
    ownership AS (
        INSERT INTO report_role_ledger
            (report_id, granted_to_user_id, set_by_user_id, role)
        SELECT new_report.report_id, :user_id, grantor.user_id, :role
        -- CROSS JOIN because `grantor` is a single row with nothing to join on
        FROM new_report CROSS JOIN grantor
        RETURNING report_id
    ),
    visibility AS (
        INSERT INTO report_visibility (report_id, set_by_user_id, public)
        SELECT new_report.report_id, grantor.user_id, FALSE
        FROM new_report CROSS JOIN grantor
        RETURNING report_id
    )
    SELECT ownership.report_id
    FROM ownership JOIN visibility ON visibility.report_id = ownership.report_id
"""


async def create_report(
    session: AsyncSession, owner_id: UUID, title: str = DEFAULT_REPORT_TITLE
) -> UUID:
    """
    Open a new report owned by `owner_id` and private to them.

    Returns the generated id. Raises `RuntimeError` if the system account the
    first grant is made by does not exist, which is a broken deployment rather
    than anything the caller did.
    """

    row: Row | None = (
        await session.execute(
            text(_CREATE_REPORT),
            {
                "title": title,
                "user_id": owner_id,
                "role": CREATOR_ROLE,
                "system_subject": SYSTEM_SUBJECT,
            },
        )
    ).one_or_none()

    if row is None:
        raise ImplementationError(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"No user with subject {SYSTEM_SUBJECT!r} to grant the first role.",
        )

    return row.report_id


MINIMUM_AUTHOR_ROLE: str = "editor"


def _authors_lateral(report_alias: str) -> str:
    """Render the join that names everyone who can currently change a report.

    Note this differs from the LATERAL subqueries in `report_access`, which
    narrow to one known user before taking the latest row. Here every grantee is
    wanted, so there is no single id to correlate on.

    The whole aggregate hangs off a LATERAL so it can see the report's id, and is
    LEFT joined so that a report whose owners have all been soft deleted still
    comes back (with no authors) rather than vanishing.

    Binds `:minimum_author_precedence`. The caller supplies it.
    """

    # Everything interpolated is a hardcoded alias from this module.
    return f"""
    LEFT JOIN LATERAL (
        SELECT array_agg(author.display_name ORDER BY current_grant.set_at)
            AS display_names
        FROM (
            SELECT DISTINCT ON (ledger.granted_to_user_id)
                ledger.granted_to_user_id, ledger.role, ledger.set_at
            FROM report_role_ledger AS ledger
            WHERE ledger.report_id = {report_alias}.report_id
            ORDER BY ledger.granted_to_user_id, ledger.set_at DESC
        ) AS current_grant

        -- Inner join removes grants to users who no longer exist
        JOIN app_user_live AS author
            ON author.user_id = current_grant.granted_to_user_id

        JOIN report_role ON report_role.role = current_grant.role

        WHERE report_role.precedence >= :minimum_author_precedence
    ) AS authors ON TRUE
"""


_REPORT_HEADER = f"""
    SELECT
        report.report_id,
        report.title,
        -- `array_agg` over no rows is NULL, not an empty array.
        COALESCE(authors.display_names, ARRAY[]::text[]) AS authors
    FROM report_live AS report

    {_authors_lateral("report")}

    WHERE report.report_id = :report_id
"""


async def get_report_header(session: AsyncSession, report_id: UUID) -> ReportHeader:
    """
    Read a report's title and the display names of everyone who can currently
    change its content, oldest grant first.

    Raises `NotFoundError` if the report does not exist or has been soft deleted.
    """

    row: Row | None = (
        await session.execute(
            text(_REPORT_HEADER),
            {
                "report_id": report_id,
                "minimum_author_precedence": await get_precedence(
                    session, REPORT_ROLE_TABLE, MINIMUM_AUTHOR_ROLE
                ),
            },
        )
    ).one_or_none()

    if row is None:
        raise NotFoundError(f"No report with id {report_id}.")

    return ReportHeader.model_validate(row)


# The base table rather than `report_live`, since writes are kept off the views,
# and `deleted_at` is checked here instead.
#
# `RETURNING` so the statement reports whether it matched anything: an UPDATE
# that hits no row is not an error to Postgres, only an empty result.
_RENAME_REPORT = """
    UPDATE report SET title = :title
    WHERE report_id = :report_id AND deleted_at IS NULL
    RETURNING report_id
"""


async def rename_report(session: AsyncSession, report_id: UUID, title: str) -> None:
    """
    Replace a report's title.

    Raises `NotFoundError` if the report does not exist or has been soft deleted.
    """

    row: Row | None = (
        await session.execute(
            text(_RENAME_REPORT), {"report_id": report_id, "title": title}
        )
    ).one_or_none()

    if row is None:
        raise NotFoundError(f"No report with id {report_id}.")


_DELETE_REPORT = """
    UPDATE report SET deleted_at = clock_timestamp()
    WHERE report_id = :report_id AND deleted_at IS NULL
    RETURNING report_id
"""


async def delete_report(session: AsyncSession, report_id: UUID) -> None:
    """
    Soft delete a report, hiding it from every read that goes through
    `report_live` without destroying it or its history.

    The report's content is deliberately left alone. Nothing can reach it once
    the report itself is gone, and leaving it untouched keeps the record of
    which blocks were already deleted beforehand intact. Restoring will be
    supported soon.

    Raises `NotFoundError` if the report does not exist or has already been soft
    deleted, which are not distinguishable from here.
    """

    row: Row | None = (
        await session.execute(text(_DELETE_REPORT), {"report_id": report_id})
    ).one_or_none()

    if row is None:
        raise NotFoundError(f"No report with id {report_id}.")


# The SELECT source rather than VALUES so that a soft deleted report inserts no
# row at all, which the caller then turns into a 404. A bare VALUES would have
# nothing to filter on and would happily record a flip on a dead report.
_SET_REPORT_VISIBILITY = """
    INSERT INTO report_visibility (report_id, set_by_user_id, public)
    SELECT report.report_id, :set_by_user_id, :public
    FROM report
    WHERE report.report_id = :report_id AND report.deleted_at IS NULL
    RETURNING report_id
"""


async def set_report_visibility(
    session: AsyncSession, report_id: UUID, public: bool, set_by_user_id: UUID
) -> None:
    """
    Record whether a report is readable by anyone, and who decided that.

    Writing the same value twice is harmless: it adds a second row saying the
    same thing, which is the history being honest about what was asked.

    Raises `NotFoundError` if the report does not exist or has been soft deleted.
    """

    row: Row | None = (
        await session.execute(
            text(_SET_REPORT_VISIBILITY),
            {
                "report_id": report_id,
                "public": public,
                "set_by_user_id": set_by_user_id,
            },
        )
    ).one_or_none()

    if row is None:
        raise NotFoundError(f"No report with id {report_id}.")


# Two stages on purpose. The CTE picks the page and nothing else, and only then
# does the outer query decorate those rows with authors and a chart. Written as
# one flat statement, the planner would be free to compute both aggregates for
# every report in the table before discarding all but a pageful.
#
# MATERIALIZED forces that. Postgres inlines a CTE that is referenced once,
# which would undo the separation.
# https://www.postgresql.org/docs/current/queries-with.html#QUERIES-WITH-CTE-MATERIALIZATION
_REPORT_PREVIEWS = f"""
    WITH page AS MATERIALIZED (
        SELECT report.report_id, report.title
        FROM report_live AS report

        LEFT JOIN LATERAL (
            SELECT history.public
            FROM report_visibility AS history
            WHERE history.report_id = report.report_id
            ORDER BY history.set_at DESC
            LIMIT 1
        ) AS visibility ON TRUE

        LEFT JOIN LATERAL (
            SELECT history.role
            FROM report_role_ledger AS history
            WHERE history.report_id = report.report_id
              AND history.granted_to_user_id = CAST(:user_id AS uuid)
            ORDER BY history.set_at DESC
            LIMIT 1
        ) AS report_grant ON TRUE

        LEFT JOIN report_role ON report_role.role = report_grant.role

        WHERE
            (
                -- Opens the range for the first page
                CAST(:cursor AS uuid) IS NULL

                -- Strictly less than, so the row the cursor names is
                -- the last of the previous page and is not served twice.
                OR report.report_id < CAST(:cursor AS uuid)
            )
            AND (
                -- A null parameter switches off a branch
                (
                    CAST(:include_public AS boolean)
                    AND COALESCE(visibility.public, FALSE)
                )
                OR report_role.precedence
                    >= CAST(:minimum_granted_precedence AS integer)
            )

        -- `report_id` is a uuidv7, so this is newest first. It is also unique,
        -- which is what lets the cursor above be a single column with no
        -- tiebreaker, and immutable, so a row never moves between pages.
        ORDER BY report.report_id DESC
        LIMIT CAST(:limit AS bigint)
    )
    SELECT
        page.report_id,
        page.title,
        -- `array_agg` over no rows is NULL, not an empty array.
        COALESCE(authors.display_names, ARRAY[]::text[]) AS authors,
        first_container.chart
    FROM page

    {_authors_lateral("page")}

    LEFT JOIN LATERAL (
        -- The first container's chart, which is not the same as the first chart
        -- in the report: if that container's block has been soft deleted this
        -- yields NULL rather than falling through to the next container. The
        -- preview is of the top of the report, whatever is there.
        SELECT chart.payload AS chart
        FROM content_mount_live AS mount
        JOIN content_container_live AS container
            ON container.container_id = mount.container_id
        LEFT JOIN blob_store_live AS chart ON chart.blob_id = container.chart_id
        WHERE mount.report_id = page.report_id
        ORDER BY mount.position
        LIMIT 1
    ) AS first_container ON TRUE

    -- Ordering is not carried out of CTEs
    ORDER BY page.report_id DESC
"""


async def get_report_previews(
    session: AsyncSession,
    *,
    user_id: UUID | None,
    include_public: bool,
    minimum_granted_precedence: int | None,
    cursor: UUID | None,
    limit: int,
) -> list[ReportPreviewRecord]:
    """
    Read one page of report previews, newest first.

    A report is included if it is public and `include_public` is set, or if
    `user_id` holds a grant on it ranking at or above
    `minimum_granted_precedence`. Passing neither criterion is not an error
    here: it honestly returns nothing, and refusing the request is the route's
    job, not this layer's.

    `cursor` is the `report_id` of the last preview the caller already has.
    Pass `None` for the first page.

    Note the caller decides what `limit` means. To learn whether a further page
    exists, ask for one more row than is wanted and check whether it arrived.
    """

    rows: Sequence[Row] = (
        await session.execute(
            text(_REPORT_PREVIEWS),
            {
                "user_id": user_id,
                "include_public": include_public,
                "minimum_granted_precedence": minimum_granted_precedence,
                "cursor": cursor,
                "limit": limit,
                "minimum_author_precedence": await get_precedence(
                    session, REPORT_ROLE_TABLE, MINIMUM_AUTHOR_ROLE
                ),
            },
        )
    ).all()

    return [ReportPreviewRecord.model_validate(row) for row in rows]
