from typing import Annotated

from fastapi import APIRouter, Query

from . import constants as const
from ...dependencies import AnalysisCatalogDep, MetricCatalogDep
from ...models import QueryParams

router: APIRouter = APIRouter()


@router.get(
    f"{const.SIMPLE_TIME_SERIES_ENDPOINT}{const.METRIC_PATH_PARAM}{const.ANALYSIS_PATH_PARAM}"
)
def simple_time_series(
    metric: str,
    analysis: str,
    query: Annotated[QueryParams, Query()],
    metric_catalog_entry: MetricCatalogDep,
    analysis_catalog_entry: AnalysisCatalogDep,
):
    return {"metric": metric, "analysis": analysis, **query.model_dump()}
