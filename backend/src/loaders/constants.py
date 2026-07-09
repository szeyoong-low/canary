from typing import Literal, Callable

from httpx import codes
from polars import LazyFrame

from ..dependencies import get_environment
from .normalise import _normalise_fmp

type ExternalAPI = Literal["FMP"]

# Dispatch tables
# The base URLs must have a trailing slash
BASE_URL: dict[ExternalAPI, str] = {"FMP": get_environment().fmp_base_url}

NORMALISER: dict[ExternalAPI, Callable[[LazyFrame], LazyFrame]] = {
    "FMP": _normalise_fmp
}

SUCCESS_STATUS_CODES: tuple = (
    codes.OK,  # 200
    codes.MOVED_PERMANENTLY,  # 301
    codes.FOUND,  # 302
    codes.TEMPORARY_REDIRECT,  # 307
    codes.PERMANENT_REDIRECT,  # 308
)
