from functools import lru_cache
from typing import Annotated

from fastapi import Depends, HTTPException
from httpx import codes

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
    try:
        return ANALYSIS_CATALOG[analysis]
    except KeyError:
        raise HTTPException(codes.INTERNAL_SERVER_ERROR, f"{analysis} is not supported")


type AnalysisCatalogDep = Annotated[AnalysisCatalogEntry, Depends(get_analysis_catalog)]


@lru_cache
def get_metric_catalog(metric: str) -> MetricCatalogEntry:
    try:
        return METRIC_CATALOG[metric]
    except KeyError:
        raise HTTPException(codes.INTERNAL_SERVER_ERROR, f"{metric} is not supported")


type MetricCatalogDep = Annotated[MetricCatalogEntry, Depends(get_metric_catalog)]
