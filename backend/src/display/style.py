from .models import ChartConfigModel
from ..types import Columns, Entities

"""Add legend and series to chart config"""


def _style_lines(
    chart_config: ChartConfigModel, columns: Columns, entities: Entities
) -> ChartConfigModel:
    return chart_config
