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
    text_id: int
    payload: str
    size_bytes: int
    created_at: datetime
    content_last_modified_at: datetime


# Mirrors the `blob_type` Postgres enum. Importing from the schema is awkward.
type BlobType = Literal["chart", "dataset"]


class BlobBlock(VersionedRecord):
    blob_id: int
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
