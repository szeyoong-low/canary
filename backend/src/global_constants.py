from re import escape
from typing import Literal

from .global_types import Column

type MetricGroup = Literal["asset-price-daily", "market-composition"]

ENTITY_TAG_SEPARATOR: str = "/"

ENTITY_TAG_REGEX: str = f"[^{ENTITY_TAG_SEPARATOR}]+{ENTITY_TAG_SEPARATOR}"

DEC_PLACES_SHOWN: int = 3

CONTENT_TYPE_HEADER: str = "Content-Type"


def column_selection_regex(
    column_name: str, tagged: Literal["tagged", "untagged", "any"]
) -> str:
    """
    If `column_name` is `foo`:
        - "tagged" matches `AAPL/foo`
        - "untagged" matches `foo`
        - "any" matches both
    """

    sanitised_column_name: str = escape(column_name)

    match tagged:
        case "tagged":
            return f"^{ENTITY_TAG_REGEX}{sanitised_column_name}$"
        case "untagged":
            return column_name
        case "any":
            return f"^({ENTITY_TAG_REGEX})?{sanitised_column_name}$"


# Allowed key columns
DATE_KEY: Column = "date"
