from fastapi import APIRouter

from .constants import *

router = APIRouter()


@router.get(f"{SIMPLE_TIME_SERIES_ENDPOINT}{METRIC_PATH_PARAM}")
def simple_time_series(metric: str):
    return metric