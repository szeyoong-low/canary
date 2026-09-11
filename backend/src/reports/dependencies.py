from typing import Annotated
from uuid import UUID

from fastapi import Depends

from ..auth.dependencies import OptionalUser
from ..db.repositories.models import ReportAccess
from ..db.repositories.report_access import get_report_access
from ..db.session import Session

"""Resolving a caller's standing on one report, once per request."""


async def resolve_report_access(
    report_id: UUID, user: OptionalUser, session: Session
) -> ReportAccess:
    """Gather everything a route needs to decide what this caller may do with this
    report. `report_id` is a path parameter"""

    return await get_report_access(
        session, report_id, user.user_id if user is not None else None
    )


# Resolved once per request even if several dependencies ask for it
type CallerReportAccess = Annotated[ReportAccess, Depends(resolve_report_access)]
