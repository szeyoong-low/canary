from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

"""The shapes that cross the repository boundary."""


class DatabaseRecord(BaseModel):
    model_config = ConfigDict(
        # Lets `model_validate` read a SQLAlchemy `Row` directly.
        # https://docs.pydantic.dev/latest/concepts/models/#arbitrary-class-instances
        from_attributes=True,
        frozen=True,  # A read is a snapshot in time
    )


class User(DatabaseRecord):
    user_id: UUID
    auth0_subject: str
    display_name: str
    created_at: datetime


class VersionedRecord(DatabaseRecord):
    """A record whose row can be updated, and therefore needs a version to guard
    against lost updates.

    Note: It versions one row. A container and the blocks it points at are
    versioned independently of each other. For now, only the blocks are versioned.
    """

    # `version` is Postgres' `xmin`: the id of the transaction that last wrote
    # the row, which changes on every update. It is read straight off the row, so
    # no column and no trigger are needed to maintain it.
    version: int


class TextBlock(VersionedRecord):
    text_id: UUID
    payload: str
    size_bytes: int
    created_at: datetime
    content_last_modified_at: datetime


# Mirrors the `blob_type` Postgres enum. Importing from the schema is awkward.
type BlobType = Literal["chart", "dataset"]


class BlobBlock(VersionedRecord):
    blob_id: UUID
    # Whatever the driver decoded the JSONB into. The repository is not the
    # layer that knows a chart config from a dataset; it stores and returns.
    payload: Any
    type: BlobType
    size_bytes: int
    created_at: datetime
    content_last_modified_at: datetime


class ReportAccess(DatabaseRecord):
    report_id: UUID
    public: bool
    # `None` means no grant was ever made: an anonymous caller, but equally a
    # signed-in one nobody has shared this report with.
    role: str | None
    precedence: int | None


class PlatformRole(DatabaseRecord):
    role: str
    precedence: int


class ReportHeader(DatabaseRecord):
    """A report's own row, plus the display names of whoever can currently
    change its content.

    Authors are folded in here rather than fetched separately because they are
    one aggregated value per report, not a collection the caller pages through.
    """

    report_id: UUID
    title: str
    # Display names, not ids: nothing downstream links to a user yet, and they
    # are not unique, so duplicates are possible and harmless.
    authors: list[str]


class ReportContentContainer(DatabaseRecord):
    """One container, with the payloads of the blocks it points at
    already resolved.

    Either payload may be `None`, meaning that block has been soft deleted. The
    container outlives its blocks, so a half-empty one is a state to render.
    """

    container_id: UUID
    # Whatever the driver decoded the JSONB into, exactly as `BlobBlock.payload`.
    # This layer does not know a chart config from any other object.
    chart: Any | None
    prose: str | None


class ReportPreviewRecord(DatabaseRecord):
    """One report as it appears in a gallery: enough to render a card and link
    to it, and nothing more.

    Deliberately not a subclass of `ReportHeader` despite the overlap. A preview
    is one row of a paginated list and a header is the top of one report, so the
    two are expected to diverge.
    """

    # Doubles as the pagination cursor. `report_id` is a uuidv7, so it sorts by
    # creation time, which is what makes keyset pagination possible here at all.
    report_id: UUID
    title: str
    authors: list[str]
    chart: Any | None
