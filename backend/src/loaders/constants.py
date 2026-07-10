from typing import Literal, Callable

from polars import LazyFrame

from ..dependencies import get_environment
from .normalise import _normalise_fmp
from ..types import Params

type ExternalAPI = Literal["FMP"]

type EndpointFMP = Literal["historical-price-eod/full"]

type ExternalEndpoint = EndpointFMP | Literal["TEST"]

# Dispatch tables
# Kept as a callable to achieve pseudo-lazy evaluation so that there is no
# coupling with the test suite, which must still evaluate it when importing.
REQUEST_HEADERS: dict[ExternalAPI, Callable[[], Params]] = {
    "FMP": (lambda: {"apikey": get_environment().fmp_api_key}),
}

# The base URLs must have a trailing slash
BASE_URL: dict[ExternalAPI, Callable[[], str]] = {
    "FMP": (lambda: get_environment().fmp_base_url),
}

NORMALISER: dict[ExternalAPI, Callable[[LazyFrame], LazyFrame]] = {
    "FMP": _normalise_fmp,
}
