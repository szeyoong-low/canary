from collections.abc import Iterable, Sequence
from functools import partial, reduce
from typing import Mapping

from asyncio import gather
from httpx import AsyncClient
from langchain_core.tools import BaseTool, tool
from polars import col, concat, LazyFrame
from polars.selectors import float as pl_float

from ..display.charts import DISPLAY_SERIES, DISPLAY_HIERARCHY
from ..display.output_models import ChartConfigModel
from ..global_constants import DEC_PLACES_SHOWN, individual_entity_regex
from ..global_types import as_awaitable, Columns
from ..loaders.constants import METRIC_GROUP_KEYS, METRIC_GROUP_BASE_METRICS
from ..loaders.load import load_asset_price_daily, load_market_composition
from .schemas import (
    AssetPriceDailyParams,
    AssetPriceDailySchema,
    MarketCompositionParams,
    MarketCompositionSchema,
)
from ..transformations.utility import (
    apply_analysis_function,
    pivot_single_entity,
    resolve_transformations,
)


@tool(args_schema=AssetPriceDailySchema)
async def asset_price_daily(**kwargs) -> ChartConfigModel:
    """
    Fetch and analyse daily price time series for one or more assets
    (stocks, indices) over a date range, returning a chart configuration.
    Use for questions about how prices, returns, or derived indicators of
    specific tickers evolve over time.
    """

    params: AssetPriceDailyParams = AssetPriceDailyParams.model_validate(kwargs)

    indiv_transforms: Iterable[str]
    collective_transforms: Iterable[str]
    indiv_transforms, collective_transforms = resolve_transformations(
        params.analysis, METRIC_GROUP_BASE_METRICS["asset-price-daily"]
    )

    keys: Columns = METRIC_GROUP_KEYS["asset-price-daily"]

    async with AsyncClient(follow_redirects=True) as client:
        indiv_entities: Iterable[LazyFrame] = await gather(
            *(
                (
                    pivot_single_entity(
                        reduce(
                            partial(
                                apply_analysis_function,
                                keys=keys,
                                params=kwargs,
                                http_client=client,
                            ),
                            indiv_transforms,
                            load_asset_price_daily(client, sym, kwargs),
                        ),
                        sym,
                        keys,
                    )
                )
                for sym in params.symbol
            )
        )

        merged_entities: LazyFrame = concat(indiv_entities, how="align_full")

        data_output: LazyFrame = (
            (
                await reduce(
                    partial(
                        apply_analysis_function,
                        keys=keys,
                        params=kwargs,
                        http_client=client,
                    ),
                    collective_transforms,
                    as_awaitable(merged_entities),
                )
            )
            .select(
                col(keys),
                col(
                    map(
                        individual_entity_regex,
                        params.analysis - set(collective_transforms),
                    )
                ),
                col(collective_transforms),
            )
            .with_columns(pl_float().round(DEC_PLACES_SHOWN))
        )

    return DISPLAY_SERIES[params.display](data_output, keys, params.symbol)


@tool(args_schema=MarketCompositionSchema)
async def market_composition(**kwargs) -> ChartConfigModel:
    """
    Break a market or index into its constituents and aggregate a metric
    across a chosen dimension, returning a hierarchical chart configuration.
    Use for questions about composition, weightings, or the contribution of
    parts to a whole at a point in time.
    """

    params: MarketCompositionParams = MarketCompositionParams.model_validate(kwargs)

    indiv_transforms: Iterable[str]
    # Collective transformations are meaningless here as all entities are
    # already in a single table
    indiv_transforms, _ = resolve_transformations(
        params.analysis, METRIC_GROUP_BASE_METRICS["market-composition"]
    )

    async with AsyncClient(follow_redirects=True) as client:
        data_output: LazyFrame = (
            (
                await reduce(
                    partial(
                        apply_analysis_function,
                        keys=[],
                        params=kwargs,
                        http_client=client,
                    ),
                    indiv_transforms,
                    load_market_composition(client, kwargs),
                )
            )
            .group_by(params.drilldown)
            .agg(
                col(params.aggregate_col).first(),
                col(params.analysis).exclude(params.aggregate_col).first(),
            )
            .with_columns(pl_float().round(DEC_PLACES_SHOWN))
        )

    return DISPLAY_HIERARCHY[params.display](
        data_output, params.drilldown, params.aggregate_col, params.colour_col
    )


# Bound to the model in the planning node and executed by the LangGraph tool node.
# The @tool decorator turns each function into a BaseTool. The description is
# read from the docstring and the interface from `args_schema`.
TERMINAL_TOOLS: Sequence[BaseTool] = [
    asset_price_daily,
    market_composition,
]

TERMINAL_TOOLS_MAPPING: Mapping[str, BaseTool] = {
    tool.name: tool for tool in TERMINAL_TOOLS
}
