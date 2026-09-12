from typing import Annotated
from uuid import UUID

from fastapi import Query
from pydantic import AfterValidator, BaseModel, ConfigDict

from ..display.output_models import ChartConfigModel
from ..global_constants import ReportRoleName
from ..validators.primitives import NonEmptyString

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
    chart: ChartConfigModel


class ReportFull(BaseReport):
    content_containers: list[DisplayedContentContainer]


class ReportMetadata(BaseModel):
    title: NonEmptyString | None = None
    public: bool | None = None


class PromptBody(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prompt: str
