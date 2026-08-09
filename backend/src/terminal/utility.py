from collections.abc import Iterable

from ..global_constants import MetricGroup
from ..global_types import Columns
from ..transformations.models import Transformation

DISPLAY_PATH_PARAM: str = "{display}"


def _get_terminal_path(metric_group: MetricGroup) -> str:
    return f"/{metric_group}/{DISPLAY_PATH_PARAM}"


def _get_shown_columns(analysis: Iterable[Transformation]) -> Columns:
    return [column.name for column in analysis if column.show]
