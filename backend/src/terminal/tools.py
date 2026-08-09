from asyncio import gather
from collections.abc import Iterable, Mapping, Sequence
from functools import partial, reduce

from httpx import AsyncClient
from langchain_core.tools import BaseTool, tool
from polars import LazyFrame, col, concat
from polars.selectors import float as pl_float

from ..display.charts import DISPLAY_HIERARCHY, DISPLAY_SERIES
from ..display.output_models import ChartConfigModel
from ..global_constants import DEC_PLACES_SHOWN, column_selection_regex
from ..global_types import Columns, as_awaitable
from ..loaders.constants import METRIC_GROUP_BASE_METRICS, METRIC_GROUP_KEYS
from ..loaders.load import load_asset_price_daily, load_market_composition
from ..transformations.models import Transformation
from ..transformations.utility import (
    apply_analysis_function,
    pivot_single_entity,
    validate_and_sort_transformations,
)
from .schemas import (
    AssetPriceDailyParams,
    AssetPriceDailySchema,
    MarketCompositionParams,
    MarketCompositionSchema,
)
from .utility import _get_shown_columns


@tool(args_schema=AssetPriceDailySchema)
async def asset_price_daily(**kwargs) -> ChartConfigModel:
    """
    Analyse daily price summary for one or more financial assets (stocks,
    indices, forex, cryptocurrencies, commodities) over a date range.

    Prompt: Compare the volume-weighted price movements of Apple, Google,
        Microsoft, Nvidia, Tesla, JP Morgan, and Bank of America from January to
        March 2026. I want to use an index that starts on the first day.

    Call: `asset-price-daily` with
    {
        "display": "time-series",
        "analysis": [
            {
                "name": "Volume-weighted average price",
                "show": false,
                "analysis": "",
                "metric": "vwap"
            },
            {
                "name": "Indexed price",
                "show": true,
                "analysis": "index-to-date",
                "metric": "Volume-weighted average price",
                "base": 100,
                "reference": "2026-01-02"
            }
        ],
        "symbol": [
            "aapl",
            "goog",
            "msft",
            "nvda",
            "tsla",
            "jpm",
            "bac"
        ],
        "start_date": "2026-01-01",
        "end_date": "2026-03-31"
    }
    """

    params: AssetPriceDailyParams = AssetPriceDailyParams.model_validate(kwargs)

    transformations: Iterable[Transformation] = validate_and_sort_transformations(
        params.analysis, METRIC_GROUP_BASE_METRICS["asset-price-daily"]
    )

    keys: Columns = METRIC_GROUP_KEYS["asset-price-daily"]

    async with AsyncClient(follow_redirects=True) as client:
        indiv_entities: Iterable[LazyFrame] = await gather(
            *(
                pivot_single_entity(
                    load_asset_price_daily(client, sym, kwargs),
                    sym,
                    keys,
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
                        shared_params=kwargs,
                        http_client=client,
                    ),
                    transformations,
                    as_awaitable(merged_entities),
                )
            )
            .select(
                col(keys),
                col(
                    map(
                        partial(
                            column_selection_regex,
                            tagged="any",
                        ),
                        _get_shown_columns(params.analysis),
                    )
                ),
            )
            .with_columns(pl_float().round(DEC_PLACES_SHOWN))
        )

    return DISPLAY_SERIES[params.display](data_output, keys, params.symbol)


@tool(args_schema=MarketCompositionSchema)
async def market_composition(**kwargs) -> ChartConfigModel:
    """
    Drill down a snapshot of public market (stocks, mutual funds,
    exchange-traded funds) to aggregate a metric on multiple dimensions.

    Prompt: Break down the market capitalisation of all public companies by
        sector, industry, then company, and show it in a treemap. Also show the
        share price of each company.

    Call: `market-composition` with
    {
        "display": "treemap",
        "analysis": [
            {
                "name": "Market capitalisation",
                "show": true,
                "analysis": "",
                "metric": "marketCap"
            },
            {
                "name": "Share price",
                "show": true,
                "analysis": "",
                "metric": "price"
            }
        ],
        "drilldown": [
            "sector",
            "industry",
            "companyName"
        ],
        "aggregate_col": "marketCap"
    }
    """

    params: MarketCompositionParams = MarketCompositionParams.model_validate(kwargs)

    transformations: Iterable[Transformation] = validate_and_sort_transformations(
        params.analysis, METRIC_GROUP_BASE_METRICS["market-composition"]
    )

    async with AsyncClient(follow_redirects=True) as client:
        data_output: LazyFrame = (
            (
                await reduce(
                    partial(
                        apply_analysis_function,
                        keys=[],
                        shared_params=kwargs,
                        http_client=client,
                    ),
                    transformations,
                    load_market_composition(client, kwargs),
                )
            )
            .group_by(params.drilldown)
            .agg(
                col(params.aggregate_col).first(),
                col(_get_shown_columns(params.analysis))
                .exclude(params.aggregate_col)
                .first(),
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
