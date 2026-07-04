from fastapi import APIRouter

from .constants import *

router = APIRouter()


@router.get(SIMPLE_TIME_SERIES_ENDPOINT)
def simple_time_series():
    return "Success"