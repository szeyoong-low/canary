from fastapi import APIRouter

from . import constants

router = APIRouter()


@router.get(f"{constants.SIMPLE_TIME_SERIES_ENDPOINT}{constants.METRIC_PATH_PARAM}")
def simple_time_series(metric: str):
    return metric
