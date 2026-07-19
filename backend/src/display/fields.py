from typing import Annotated

from pydantic import AfterValidator

MIN_RGB: int = 0
MAX_RGB: int = 255


def _validate_rgb(n: int) -> int:
    if MIN_RGB <= n <= MAX_RGB:
        return n

    raise ValueError(f"{n} must lie between {MIN_RGB} and {MAX_RGB} inclusive")


type ByteField = Annotated[int, AfterValidator(_validate_rgb)]

NORMALISED_FLOOR: float = 0
NORMALISED_CEILING: float = 1


def _validate_normalised_float(x: float) -> float:
    if NORMALISED_FLOOR <= x <= NORMALISED_CEILING:
        return x

    raise ValueError(
        f"{x} must lie between {NORMALISED_FLOOR} and {NORMALISED_CEILING} inclusive"
    )


type NormalisedFloatField = Annotated[float, AfterValidator(_validate_normalised_float)]

HEX_PREFIX: str = "#"


def _validate_hex_string(string: str) -> str:
    if (
        (len(string) in (4, 7))
        and string[0] == HEX_PREFIX
        and all((c.isalnum() for c in string[1:]))
    ):
        return string

    raise ValueError(f"{string} is not in the format #ABC or #ABC123")


type HexColor = Annotated[str, AfterValidator(_validate_hex_string)]

type Number = int | float


def _validate_non_negative_number(n: Number) -> Number:
    if n > 0:
        return n

    raise ValueError(f"{n} must be a positive number")


type NonNegativeNumberField = Annotated[
    Number, AfterValidator(_validate_non_negative_number)
]
