from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from ..catalog import (
    AnalysisCatalogEntry,
    ANALYSIS_CATALOG,
    MetricCatalogEntry,
    METRIC_CATALOG,
)
from .environment import Environment


"""For dependency injection, as shown in https://fastapi.tiangolo.com/advanced/settings/#lru-cache-technical-details"""


@lru_cache
def get_environment() -> Environment:
    return Environment()  # pyright: ignore[reportCallIssue] (Initialised by pydantic_settings)


@lru_cache
def get_analysis_catalog(analysis: str) -> AnalysisCatalogEntry:
    return ANALYSIS_CATALOG[analysis]


type AnalysisCatalogDep = Annotated[AnalysisCatalogEntry, Depends(get_analysis_catalog)]


@lru_cache
def get_metric_catalog(metric: str) -> MetricCatalogEntry:
    return METRIC_CATALOG[metric]


type MetricCatalogDep = Annotated[MetricCatalogEntry, Depends(get_metric_catalog)]
