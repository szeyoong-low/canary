from typing import Literal, Callable

from polars import LazyFrame
from httpx import codes

from .normalise import _normalise_fmp
from ..dependencies import get_environment

type ExternalAPI = Literal["FMP"]

# Dispatch tables
BASE_URL: dict[ExternalAPI, Callable[[], str]] = {
    "FMP": (lambda: get_environment().fmp_base_url)
}

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

# For unpivoting
KEY_COLUMN_NAME: str = "key"
VALUE_COLUMN_NAME: str = "value"
