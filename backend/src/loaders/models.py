from typing import Literal

from ..validators.primitives import QueryBaseModel


class MarketComposition(QueryBaseModel):
    category: Literal["company", "etf", "fund"] = "company"
    industry: list[str] = []
    sector: list[str] = []
    exchange: list[str] = []
    country: list[str] = []
