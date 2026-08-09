from inspect import cleandoc
from typing import Annotated

from pydantic import Field

from ..analysis.aggregate import AnyAggregateFunction
from ..analysis.individual import AnyLinearFunction
from ..analysis.models import UNION_DISCRIMINATOR, BaseMetric
from ..display.charts import HierarchyDisplayName, SeriesDisplayName
from ..global_types import Column, ColumnOptional
from ..loaders.constants import (
    ASSET_PRICE_DAILY_BASE_METRICS,
    MARKET_COMPOSITION_BASE_METRICS,
)
from ..loaders.models import MarketCompositionFilters
from ..validators.primitives import DateRange, ParamBaseModel
from .models import MARKET_DRILLDOWN, EntityParam, MarketDrilldownParam

"""Pydantic models that form schemas for terminal functions used as agent tools."""


class AssetPriceDailyParams(ParamBaseModel):
    display: SeriesDisplayName

    analysis: list[
        Annotated[
            BaseMetric | AnyLinearFunction | AnyAggregateFunction,
            Field(
                discriminator=UNION_DISCRIMINATOR,
                description=cleandoc(f"""
                    Base metrics available: {ASSET_PRICE_DAILY_BASE_METRICS},
                    where `vwap` is the volume-weighted average price
                """),
            ),
        ]
    ]

    symbol: EntityParam
    """Ticker symbols of individual entites, e.g. AAPL for Apple inc., ^VIX for
    the CBOE market volatility index"""


class AssetPriceDailySchema(AssetPriceDailyParams, DateRange):
    pass


class MarketCompositionParams(ParamBaseModel):
    display: HierarchyDisplayName

    analysis: list[
        Annotated[
            BaseMetric | AnyLinearFunction,
            Field(
                discriminator=UNION_DISCRIMINATOR,
                description=cleandoc(f"""
                    Base metrics available: {MARKET_COMPOSITION_BASE_METRICS}
                """),
            ),
        ]
    ]

    drilldown: Annotated[
        MarketDrilldownParam,
        Field(
            description=cleandoc(f"""One or many of {MARKET_DRILLDOWN}, from most
            high-level to most granular, e.g. [sector, industry, companyName]""")
        ),
    ]

    aggregate_col: Column
    """Numeric metric (must be one of the analysis functions applied) that
    drives the relative size of chart elements. No need to repeat in `analysis`"""

    colour_col: ColumnOptional = None
    """Numeric metric (must be one of the analysis functions applied) that
    drives the colouring according to a colour bar. If None, the highest level
    drilldown determines the hue and the next drilldown determines the tint."""


class MarketCompositionSchema(MarketCompositionParams, MarketCompositionFilters):
    pass
