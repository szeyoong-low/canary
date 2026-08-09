from collections.abc import Iterable

from ..analysis.models import Transformation
from ..global_types import Columns


def _get_shown_columns(analysis: Iterable[Transformation]) -> Columns:
    return [column.name for column in analysis if column.show]
