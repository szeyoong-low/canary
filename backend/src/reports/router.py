from typing import Literal
from uuid import UUID, uuid4

from fastapi import APIRouter, status

from . import types

router = APIRouter(prefix="/reports")

REPORT_ID_PATH_PARAM_SEGMENT: str = "/{report_id}"

DEFAULT_PAGINATION_PAGE_SIZE: int = 10


@router.post("/")
def create_new_report() -> UUID:
    return uuid4()


@router.get("/previews")
def get_report_previews(
    visibility: Literal["public", "private", "any"] = "any",
    minimum_report_role: types.MinimumReportRole | None = None,
    cursor: UUID | None = None,
    page_size: types.PageSizeParam = DEFAULT_PAGINATION_PAGE_SIZE,
) -> list[types.ReportPreview]:
    print(
        {
            "visibility": visibility,
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


@router.patch(REPORT_ID_PATH_PARAM_SEGMENT, status_code=status.HTTP_204_NO_CONTENT)
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
