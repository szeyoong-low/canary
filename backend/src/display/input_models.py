from ..global_types import Column, ColumnOptional
from ..validators.primitives import QueryBaseModel


class HierarchyInputModel(QueryBaseModel):
    aggregate_col: Column
    colour_col: ColumnOptional = None
