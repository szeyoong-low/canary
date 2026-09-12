from uuid import UUID

from fastapi import APIRouter, Response, status

from ...src.auth.dependencies import CurrentUser
from ..db.repositories.reports import create_report
from ..db.session import DBSession
from ..global_constants import LOCATION_HEADER
from . import types

REPORTS_PATH_PREFIX: str = "/reports"

router = APIRouter(prefix=REPORTS_PATH_PREFIX)

REPORT_ID_PATH_PARAM_SEGMENT: str = "/{report_id}"

DEFAULT_PAGINATION_PAGE_SIZE: int = 10


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
    response: Response, user: CurrentUser, session: DBSession
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


@router.get(REPORT_ID_PATH_PARAM_SEGMENT)
def get_specific_report(report_id: UUID) -> types.ReportFull:
    print(report_id)
    return types.ReportFull(
        title="foo",
        authors=["foo"],
        content_containers=[],
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
        chart=types.ChartConfigModel(),
        prose="",
    )
