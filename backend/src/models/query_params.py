from datetime import date

from pydantic import BaseModel


class QueryParams(BaseModel):
    model_config = {"extra": "forbid"}

    symbols: list[str]
    start_date: date
    end_date: date
