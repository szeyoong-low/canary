from typing import Literal

from ..validators.primitives import ParamBaseModel


class MarketComposition(ParamBaseModel):
    category: Literal["company", "etf", "fund"] = "company"
    industry: list[str] = []
    sector: list[str] = []
    exchange: list[str] = []
    country: list[str] = []
