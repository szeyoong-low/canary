from typing import Annotated

from pydantic import AfterValidator


def _check_positive_int(n: int) -> int:
    if n > 0:
        return n

    raise ValueError(f"{n} must be a positive integer")


type PositiveInt = Annotated[int, AfterValidator(_check_positive_int)]
