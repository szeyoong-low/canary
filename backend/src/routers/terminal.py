from collections.abc import Iterable
from functools import partial, reduce

from asyncio import gather
from fastapi import APIRouter, Request
from httpx import AsyncClient
from polars import concat, LazyFrame
from starlette.datastructures import QueryParams

from ..loaders.constants import METRIC_GROUP_KEYS, METRIC_GROUP_BASE_METRICS
from ..loaders.load import load_asset_price_daily
from ..transformations.utility import (
    apply_analysis_function,
    pivot_single_entity,
    resolve_transformations,
)
from ..types import as_awaitable, Columns
from .utility import _get_terminal_path, SetQueryParam

router = APIRouter(prefix="/terminal")


@router.get(_get_terminal_path("asset-price-daily"))
async def asset_price_daily_handler(
    display: str,
    analysis: SetQueryParam,
    symbol: SetQueryParam,
    request: Request,
):

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
                        analysis - set(collective_transforms),
                    )
                )
                for sym in symbol
            )
        )

        merged_entities: LazyFrame = concat(indiv_entities, how="align_full")

        data_output: LazyFrame = await reduce(
            partial(
                apply_analysis_function,
                keys=keys,
                query_params=query_params,
                http_client=client,
            ),
            collective_transforms,
            as_awaitable(merged_entities),
        )

        print(data_output.collect())

    return {
        "metric_group": "asset-price-daily",
        "display": display,
        "analysis": analysis,
        "symbol": symbol,
    }
