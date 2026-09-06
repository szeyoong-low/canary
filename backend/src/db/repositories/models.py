from datetime import datetime
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
