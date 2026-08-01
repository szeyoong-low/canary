from typing import Literal

from .global_types import Column, Params

type MetricGroup = Literal["asset-price-daily", "market-composition"]

TRANSFORMATION_SEPARATOR: str = "/"

INITIAL_METRIC_SEPARATOR: str = ","

DOCS_ITEM_SEPARATOR: str = ", "

EMPTY_STRING: str = ""

DEC_PLACES_SHOWN: int = 3


# Polars takes regular expressions as strings
# Prepend this to `foo/bar/baz` to match `AAPL/foo/bar/baz`
def individual_entity_regex(column_name: str) -> str:
    return f"^[^{TRANSFORMATION_SEPARATOR}]+/{column_name}$"


def collect_documentation(dispatch_table: Params):
    return DOCS_ITEM_SEPARATOR.join(
        f"{name}: {function.__doc__}" for name, function in dispatch_table.items()
    )


# Allowed key columns
DATE_KEY: Column = "date"
