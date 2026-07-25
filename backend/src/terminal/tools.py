from collections.abc import Iterable
from functools import partial, reduce

from asyncio import gather
from httpx import AsyncClient
from polars import col, concat, LazyFrame
from polars.selectors import float as pl_float

from ..display.charts import DISPLAY_SERIES, DISPLAY_HIERARCHY
from ..display.output_models import ChartConfigModel
from ..global_constants import (
    DEC_PLACES_SHOWN,
    individual_entity_regex,
)
from ..global_types import as_awaitable, Columns
from ..loaders.constants import METRIC_GROUP_KEYS, METRIC_GROUP_BASE_METRICS
from ..loaders.load import load_asset_price_daily, load_market_composition
from .schemas import AssetPriceDailyParams, MarketCompositionParams
from ..transformations.utility import (
    apply_analysis_function,
    pivot_single_entity,
    resolve_transformations,
)


async def asset_price_daily(**kwargs) -> ChartConfigModel:
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


async def market_composition(
    **kwargs,
) -> ChartConfigModel:
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
