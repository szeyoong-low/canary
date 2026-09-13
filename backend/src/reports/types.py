from typing import Annotated
from uuid import UUID

from fastapi import Query
from pydantic import AfterValidator, BaseModel, ConfigDict, Field

from ..display.output_models import ChartConfigModel
from ..global_constants import ReportRoleName
from ..validators.primitives import NonEmptyString


class StrictBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


PAGE_SIZE_MIN: int = 1
PAGE_SIZE_MAX: int = 100


def _valid_page_size(n: int) -> int:
    if PAGE_SIZE_MIN <= n <= PAGE_SIZE_MAX:
        return n

    raise ValueError(
        f"Page size must be between {PAGE_SIZE_MIN} and {PAGE_SIZE_MAX} inclusive"
    )


type PageSizeParam = Annotated[int, Query(), AfterValidator(_valid_page_size)]

# Must keep in sync with seed.__main__.py
type MinimumReportRole = Annotated[ReportRoleName, Query()]


class DisplayedContentContainer(BaseModel):
    # Exposed so clients can identify a container across refetches.
    # Positions are not stable, since containers can be reordered and
    # unmounted into the report's recycling bin.
    container_id: UUID
    # Both nullable: a block can be deleted while its container stays mounted,
    # and the client shows what is left rather than the container disappearing.
    chart: ChartConfigModel | None
    prose: str | None


class BaseReport(BaseModel):
    title: NonEmptyString
    authors: list[
        NonEmptyString
    ]  # May contain duplicates as display names are not unique


class ReportPreview(BaseReport):
    # The link target for the card, and the cursor that asks for the page after
    # this one. One value serving both is a property of `report_id` being a
    # uuidv7: it identifies the report and orders it at the same time.
    report_id: UUID
    chart: ChartConfigModel | None  # First chart of the report


class ReportPreviewPage(BaseModel):
    """One page of a gallery, and how to ask for the next."""

    previews: list[ReportPreview]
    next_cursor: UUID | None  # `None` means this was the last page


class ReportFull(BaseReport):
    public: bool
    content_containers: list[DisplayedContentContainer]


class ReportTitle(StrictBaseModel):
    title: NonEmptyString


class ReportVisibility(StrictBaseModel):
    public: bool


# Long enough for a detailed question, short enough that a pasted transcript
# (the usual shape of a prompt injection payload) is rejected before it reaches
# the model. Also caps what one request can cost in input tokens
PROMPT_MAX_LENGTH: int = 2000


class PromptBody(StrictBaseModel):
    prompt: Annotated[NonEmptyString, Field(max_length=PROMPT_MAX_LENGTH)]
