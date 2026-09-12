from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Response, status

from ...src.auth.dependencies import CurrentUser
from ..db.repositories.models import ReportContentContainer, ReportHeader
from ..db.repositories.report_contents import get_report_containers
from ..db.repositories.reports import create_report, get_report_header
from ..db.session import DBSession
from ..global_constants import LOCATION_HEADER
from . import types
from .dependencies import require_report_role

REPORTS_PATH_PREFIX: str = "/reports"

router = APIRouter(prefix=REPORTS_PATH_PREFIX)

REPORT_ID_PATH_PARAM_SEGMENT: str = "/{report_id}"

DEFAULT_PAGINATION_PAGE_SIZE: int = 10

# Public reports grant it implicitly
READER_ROLE: types.ReportRole = "viewer"


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
def get_report_previews(
    public: bool | None = None,
    minimum_report_role: types.MinimumReportRole | None = None,
    cursor: UUID | None = None,
    page_size: types.PageSizeParam = DEFAULT_PAGINATION_PAGE_SIZE,
) -> list[types.ReportPreview]:
    print(
        {
            "public": public,
            "minimum_report_role": minimum_report_role,
            "cursor": cursor,
            "page_size": page_size,
        }
    )
    return []


@router.get(
    REPORT_ID_PATH_PARAM_SEGMENT,
    dependencies=[Depends(require_report_role(READER_ROLE))],
)
async def get_specific_report(report_id: UUID, session: DBSession) -> types.ReportFull:
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
        authors=header.authors,
        content_containers=[
            types.DisplayedContentContainer(
                container_id=container.container_id,
                chart=types.ChartConfigModel.model_validate(container.chart),
                prose=container.prose,
            )
            for container in containers
        ],
    )


@router.patch(
    REPORT_ID_PATH_PARAM_SEGMENT,
    status_code=status.HTTP_204_NO_CONTENT,
    # A 204 is already bodyless, but the default response class would still
    # label it `application/json`. See `create_new_report` above.
    response_class=Response,
)
def update_report_metadata(
    report_id: UUID, updated_metadata: types.ReportMetadata
) -> None:
    """
    Since metadata changes are very straightforward, a 204 is sufficient to
    confirm success. No need to waste bandwidth returning the entire report.
    https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods/PATCH
    """

    print(
        {
            "report_id": report_id,
            "updated_metadata": updated_metadata,
        }
    )


@router.post(f"{REPORT_ID_PATH_PARAM_SEGMENT}/contents")
def add_generated_content_to_report(
    report_id: UUID,
    prompt_body: types.PromptBody,
) -> types.DisplayedContentContainer:
    print(
        {
            "report_id": report_id,
            "prompt_body": prompt_body,
        }
    )
    return types.DisplayedContentContainer(
        # Placeholder while this endpoint is a stub. The real value is the
        # uuidv7 Postgres assigns to `content_container.container_id`.
        container_id=uuid4(),
        chart=types.ChartConfigModel(),
        prose="",
    )
