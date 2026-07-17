from collections.abc import Iterable
from functools import partial
from typing import Annotated

from fastapi import Query
from pydantic import AfterValidator, BeforeValidator

from ..global_constants import INITIAL_METRIC_SEPARATOR


def _uppercasify_sort_strings(strings: Iterable[str]) -> list[str]:
    uppercased: set[str] = set()

    for s in strings:
        uppercased.add(s.upper())

    return sorted(uppercased)


type EntityQueryParam = Annotated[
    list[str], Query(), AfterValidator(_uppercasify_sort_strings)
]

type SetQueryParam = Annotated[set[str], Query()]


type SequenceQueryParam[T] = Annotated[
    list[T], Query(), BeforeValidator(partial(str.split, sep=INITIAL_METRIC_SEPARATOR))
]
