from collections.abc import Iterable
from functools import partial
from typing import Annotated

from pydantic import AfterValidator, BeforeValidator

from ..global_types import Columns


def _uppercasify_sort_strings(strings: Iterable[str]) -> list[str]:
    uppercased: set[str] = set()

    for s in strings:
        uppercased.add(s.upper())

    return sorted(uppercased)


type EntityParam = Annotated[list[str], AfterValidator(_uppercasify_sort_strings)]


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

DRILLDOWN_SEPARATOR: str = ","


type MarketDrilldownParam = Annotated[
    list[str],
    BeforeValidator(partial(_split_on_separator, sep=DRILLDOWN_SEPARATOR)),
    AfterValidator(partial(_all_valid_columns, columns=MARKET_DRILLDOWN)),
]
