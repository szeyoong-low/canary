from typing import Literal


type MetricGroup = Literal["asset-price-daily"]

TRANSFORMATION_SEPARATOR: str = "/"

INITIAL_METRIC_SEPARATOR: str = "+"

EMPTY_STRING: str = ""


# Polars takes regular expressions as strings
# Prepend this to `foo/bar/baz` to match `AAPL/foo/bar/baz`
def individual_entity_regex(column_name: str) -> str:
    return f"^[^{TRANSFORMATION_SEPARATOR}]+/{column_name}$"
