from typing import Literal

from .global_types import Column


type MetricGroup = Literal["asset-price-daily", "market-composition"]

TRANSFORMATION_SEPARATOR: str = "/"

INITIAL_METRIC_SEPARATOR: str = ","

EMPTY_STRING: str = ""

DEC_PLACES_SHOWN: int = 3


# Polars takes regular expressions as strings
# Prepend this to `foo/bar/baz` to match `AAPL/foo/bar/baz`
def individual_entity_regex(column_name: str) -> str:
    return f"^[^{TRANSFORMATION_SEPARATOR}]+/{column_name}$"


# Allowed key columns
DATE_KEY: Column = "date"
