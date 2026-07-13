from collections.abc import Iterable
from typing import Annotated

from fastapi import Query
from httpx import codes
from pydantic import AfterValidator

from ..constants import MetricGroup
from ..display.charts import DISPLAY_FUNCTIONS


DISPLAY_PATH_PARAM: str = "{display}"


def _get_terminal_path(metric_group: MetricGroup) -> str:
    return f"/{metric_group}/{DISPLAY_PATH_PARAM}"


def _validate_display(display: str) -> str:
    if display not in DISPLAY_FUNCTIONS:
        raise ValueError(
            codes.UNPROCESSABLE_ENTITY,
            f"{display} is not a valid display function",
        )

    return display


def _uppercasify_sort_strings(strings: Iterable[str]) -> list[str]:
    uppercased: set[str] = set()

    for s in strings:
        uppercased.add(s.upper())

    return sorted(uppercased)


type DisplayPathParam = Annotated[str, AfterValidator(_validate_display)]
type SetQueryParam = Annotated[set[str], Query()]
type EntityQueryParam = Annotated[
    list[str], Query(), AfterValidator(_uppercasify_sort_strings)
]
