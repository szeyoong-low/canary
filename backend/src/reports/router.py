from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status

from ..agent.invoke import invoke_agent
from ..auth.dependencies import ActiveUser, CurrentUser, require_platform_role
from ..db.repositories.models import (
    ReportAccess,
    ReportContentContainer,
    ReportHeader,
    ReportPreviewRecord,
)
from ..db.repositories.report_contents import (
    create_mounted_container,
    get_report_containers,
)
from ..db.repositories.reports import (
    create_report,
    get_report_header,
    get_report_previews,
    rename_report,
    set_report_visibility,
)
from ..db.repositories.role_vocabulary import REPORT_ROLE_TABLE, get_precedence
from ..db.session import DBSession
from ..global_constants import LOCATION_HEADER, PlatformRoleName, ReportRoleName
from ..terminal.utility import TerminalToolResult
from ..validators.primitives import NonNegativeInt
from . import types
from .dependencies import require_report_role

REPORTS_PATH_PREFIX: str = "/reports"

router = APIRouter(prefix=REPORTS_PATH_PREFIX)

REPORT_ID_PATH_PARAM_SEGMENT: str = "/{report_id}"

DEFAULT_PAGINATION_PAGE_SIZE: int = 10

READER_ROLE: ReportRoleName = "viewer"  # Public reports grant it implicitly
WRITER_ROLE: ReportRoleName = "editor"
OWNER_ROLE: ReportRoleName = "owner"
ACTIVE_ROLE: PlatformRoleName = "app_user"


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    # The default `JSONResponse` would send the literal body `null` under a JSON
    # content type, and advertise an untyped body in the schema. A bare
    # `Response` sends neither, so the contract and the wire agree.
    response_class=Response,
    # Declared to let the frontend's generated types expose `Location` as the
    # place the new report can be found.
    # https://fastapi.tiangolo.com/advanced/additional-responses/
    responses={
        status.HTTP_201_CREATED: {
            "headers": {
                LOCATION_HEADER: {
                    "description": "Where the newly created report can be found.",
                    # Not `format: uri` because generators render both as
                    # `string` and the extra keyword suggests a validation
                    # this API does not perform.
                    "schema": {"type": "string"},
                }
            }
        }
    },
    dependencies=[Depends(require_platform_role("app_user"))],
)
async def create_new_report(
    user: CurrentUser, session: DBSession, response: Response
) -> None:
    """
    Open an empty report owned by the caller and private to them.

    Nothing is returned but the `Location` of the new report, which is all the
    frontend needs to navigate to it.
    """

    report_id: UUID = await create_report(
        session,
        user.user_id,
    )

    # React router can handle relative paths
    response.headers[LOCATION_HEADER] = f"{REPORTS_PATH_PREFIX}/{report_id}"


@router.get("/previews")
async def list_report_previews(
    user: ActiveUser,
    session: DBSession,
    public: bool = False,
    minimum_report_role: types.MinimumReportRole | None = None,
    cursor: UUID | None = None,
    page_size: types.PageSizeParam = DEFAULT_PAGINATION_PAGE_SIZE,
) -> types.ReportPreviewPage:
    """
    One page of report previews, newest first.

    The two criteria are a union, not an intersection.

    `cursor` is the `report_id` of the last preview already held. Omit it for
    the first page, and stop when the response carries no `next_cursor`.
    """

    if not public and minimum_report_role is None:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Ask for public reports, a minimum report role, or both.",
        )

    records: list[ReportPreviewRecord] = await get_report_previews(
        session,
        user_id=user.user_id if user is not None else None,
        include_public=public,
        minimum_granted_precedence=(
            await get_precedence(session, REPORT_ROLE_TABLE, minimum_report_role)
            if minimum_report_role is not None and user is not None
            else None
        ),
        cursor=cursor,
        limit=page_size + 1,  # One more than asked for, to get the next cursor
    )

    page: list[ReportPreviewRecord] = records[:page_size]

    return types.ReportPreviewPage(
        previews=[
            types.ReportPreview(
                report_id=record.report_id,
                title=record.title,
                authors=record.authors,
                chart=(
                    types.ChartConfigModel.model_validate(record.chart)
                    if record.chart is not None
                    else None
                ),
            )
            for record in page
        ],
        next_cursor=page[-1].report_id if len(records) > page_size else None,
    )


@router.get(REPORT_ID_PATH_PARAM_SEGMENT)
async def get_specific_report(
    report_id: UUID,
    session: DBSession,
    access: Annotated[ReportAccess, Depends(require_report_role(READER_ROLE))],
) -> types.ReportFull:
    """
    Read one report in full: its metadata and every container mounted in it.

    A report that does not exist, or that this caller may not read, never
    reaches this body. The guard above answers both.
    """

    # They are awaited in sequence, not gathered, as a session is a single
    # connection and cannot run two statements at once.
    header: ReportHeader = await get_report_header(session, report_id)
    containers: list[ReportContentContainer] = await get_report_containers(
        session, report_id
    )

    return types.ReportFull(
        title=header.title,
        public=access.public,
        authors=header.authors,
        content_containers=[
            types.DisplayedContentContainer(
                container_id=container.container_id,
                chart=(
                    types.ChartConfigModel.model_validate(container.chart)
                    if container.chart is not None
                    else None
                ),
                prose=container.prose,
            )
            for container in containers
        ],
    )


@router.put(
    f"{REPORT_ID_PATH_PARAM_SEGMENT}/title",
    status_code=status.HTTP_204_NO_CONTENT,
    # A 204 is already bodyless, but the default response class would still
    # label it `application/json`. See `create_new_report` above.
    response_class=Response,
    dependencies=[
        Depends(require_report_role(WRITER_ROLE)),
        Depends(require_platform_role(ACTIVE_ROLE)),
    ],
)
async def rename_specific_report(
    report_id: UUID, new_title: types.ReportTitle, session: DBSession
) -> None:
    """
    Retitle a report.

    A 204 is enough to confirm it: the caller already knows the title it sent,
    so returning the report again would only waste bandwidth.
    """

    await rename_report(session, report_id, new_title.title)


@router.put(
    f"{REPORT_ID_PATH_PARAM_SEGMENT}/visibility",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    dependencies=[
        Depends(require_report_role(OWNER_ROLE)),
        Depends(require_platform_role(ACTIVE_ROLE)),
    ],
)
async def publish_or_unpublish_report(
    report_id: UUID,
    new_visibility: types.ReportVisibility,
    user: CurrentUser,
    session: DBSession,
) -> None:
    """
    Publish a report to everyone, or take it private again.

    The caller is recorded alongside the flip: `report_visibility` is an
    append-only history, and who published a report is part of what it answers.
    """

    await set_report_visibility(session, report_id, new_visibility.public, user.user_id)


@router.post(
    f"{REPORT_ID_PATH_PARAM_SEGMENT}/contents",
    dependencies=[
        Depends(require_report_role(WRITER_ROLE)),
        Depends(require_platform_role(ACTIVE_ROLE)),
    ],
)
async def add_generated_content_to_report(
    report_id: UUID,
    prompt_body: types.PromptBody,
    session: DBSession,
    position: NonNegativeInt | None = None,
) -> types.DisplayedContentContainer:
    result: TerminalToolResult = await invoke_agent(prompt_body.prompt)

    container_id: UUID = await create_mounted_container(
        session,
        report_id,
        result["chart"],
        result["dataset"],
        prompt_body.prompt,
        position,
    )

    return types.DisplayedContentContainer(
        container_id=container_id,
        chart=result["chart"],
        prose=prompt_body.prompt,
    )
