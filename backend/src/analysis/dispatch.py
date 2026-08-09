from ..analysis.aggregate import GROUP_MEAN, group_mean
from ..analysis.constants import AnalysisFunctionDispatch
from ..analysis.individual import (
    BASE_METRIC,
    INDEX_TO_DATE,
    RETURNS,
    VOLATILITY,
    base_metric,
    index_to_date,
    returns,
    volatility,
)

ANALYSIS_FUNCTION_DISPATCH: AnalysisFunctionDispatch = {
    BASE_METRIC: base_metric,
    VOLATILITY: volatility,
    RETURNS: returns,
    INDEX_TO_DATE: index_to_date,
    GROUP_MEAN: group_mean,
}
