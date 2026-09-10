from typing import Annotated, Literal

from fastapi import Query
from pydantic import BaseModel, ConfigDict

from ..display.output_models import ChartConfigModel
from ..validators.primitives import NonEmptyString, PositiveInt

type PageSizeParam = Annotated[PositiveInt, Query()]
# Must keep in sync with seed.__main__.py
type MinimumReportRole = Annotated[
    Literal["viewer", "commenter", "editor", "owner"], Query()
]


class DisplayedContentContainer(BaseModel):
    chart: ChartConfigModel
    prose: str


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
