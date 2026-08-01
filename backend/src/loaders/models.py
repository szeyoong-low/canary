from typing import Literal

from pydantic import Field

from ..validators.primitives import ParamBaseModel


class MarketComposition(ParamBaseModel):
    category: Literal["company", "etf", "fund"] = "company"
    industry: list[str] = Field(default=[])
    sector: list[str] = Field(default=[])
    exchange: list[str] = Field(default=[])
    country: list[str] = Field(default=[])
