from collections.abc import Iterable

from ..global_types import Columns
from ..transformations.models import Transformation


def _get_shown_columns(analysis: Iterable[Transformation]) -> Columns:
    return [column.name for column in analysis if column.show]
