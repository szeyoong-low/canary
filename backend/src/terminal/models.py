from collections.abc import Iterable
from functools import partial
from typing import Annotated

from fastapi import Query
from pydantic import AfterValidator, BeforeValidator

from ..global_constants import INITIAL_METRIC_SEPARATOR
from ..global_types import Columns


def _uppercasify_sort_strings(strings: Iterable[str]) -> list[str]:
    uppercased: set[str] = set()

    for s in strings:
        uppercased.add(s.upper())

    return sorted(uppercased)


type EntityQueryParam = Annotated[
    list[str], Query(), AfterValidator(_uppercasify_sort_strings)
]

type SetQueryParam = Annotated[set[str], Query()]


def _all_valid_columns(strings: list[str], columns: Columns) -> list[str]:
    if not all(string in columns for string in strings):
        raise ValueError(f"Must be one of {MARKET_DRILLDOWN}")
    return strings


def _split_on_separator(value: list[str] | str, sep: str):
    """For use in situations where the BeforeValidator is to turn a string into a list"""

    if isinstance(value, list):
        return [item for s in value for item in s.split(sep)]
    if isinstance(value, str):
        return value.split(sep)


MARKET_DRILLDOWN: Columns = {
    "country",
    "exchange",
    "exchangeShortName",
    "industry",
    "sector",
    "symbol",
    "companyName",
}


type MarketDrilldownQueryParam = Annotated[
    list[str],
    Query(),
    BeforeValidator(partial(_split_on_separator, sep=INITIAL_METRIC_SEPARATOR)),
    AfterValidator(partial(_all_valid_columns, columns=MARKET_DRILLDOWN)),
]
