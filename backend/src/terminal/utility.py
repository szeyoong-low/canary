from collections.abc import Iterable
from typing import TypedDict

from ..analysis.models import AnalysisFunction
from ..display.output_models import ChartConfigModel
from ..global_types import Columns, DatasetType


class TerminalToolResult(TypedDict):
    chart: ChartConfigModel
    dataset: DatasetType


def _get_shown_columns(analysis: Iterable[AnalysisFunction]) -> Columns:
    return [column.name for column in analysis if column.show]
