from collections.abc import Iterable
from functools import partial, reduce

from asyncio import gather
from fastapi import APIRouter, Request
from httpx import AsyncClient
from polars import col, concat, LazyFrame
from polars.selectors import float as pl_float
from starlette.datastructures import QueryParams

from ..display.charts import DISPLAY_FUNCTIONS
from ..display.models import ChartConfigModel
from ..global_constants import DEC_PLACES_SHOWN, individual_entity_regex
from ..global_types import as_awaitable, Columns
from ..loaders.constants import METRIC_GROUP_KEYS, METRIC_GROUP_BASE_METRICS
from ..loaders.load import load_asset_price_daily
from ..transformations.utility import (
    apply_analysis_function,
    pivot_single_entity,
    resolve_transformations,
)
from .utility import (
    DisplayPathParam,
    EntityQueryParam,
    _get_terminal_path,
    SetQueryParam,
)

router = APIRouter(prefix="/terminal")


@router.get(_get_terminal_path("asset-price-daily"))
async def asset_price_daily_handler(
    display: DisplayPathParam,
    analysis: SetQueryParam,
    symbol: EntityQueryParam,
    request: Request,
) -> ChartConfigModel:

    indiv_transforms: Iterable[str]
    collective_transforms: Iterable[str]
    indiv_transforms, collective_transforms = resolve_transformations(
        analysis, METRIC_GROUP_BASE_METRICS["asset-price-daily"]
    )

    query_params: QueryParams = request.query_params
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
                                query_params=query_params,
                                http_client=client,
                            ),
                            indiv_transforms,
                            load_asset_price_daily(client, sym, query_params),
                        ),
                        sym,
                        keys,
                    )
                )
                for sym in symbol
            )
        )

        merged_entities: LazyFrame = concat(indiv_entities, how="align_full")

        data_output: LazyFrame = (
            (
                await reduce(
                    partial(
                        apply_analysis_function,
                        keys=keys,
                        query_params=query_params,
                        http_client=client,
                    ),
                    collective_transforms,
                    as_awaitable(merged_entities),
                )
            )
            .select(
                col(keys),
                col(
                    map(individual_entity_regex, analysis - set(collective_transforms))
                ),
                col(collective_transforms),
            )
            .with_columns(pl_float().round(DEC_PLACES_SHOWN))
        )

    return DISPLAY_FUNCTIONS[display](data_output.collect(), keys, symbol)
