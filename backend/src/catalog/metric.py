from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..models import QueryParams

# Imported for the type annotation only. A runtime import would close the cycle
# catalog -> loaders.constants -> dependencies -> catalog. `from __future__ import
# annotations` turns annotations into strings, so ExternalAPI is never needed at
# runtime here (the stored value is just the literal "FMP").
if TYPE_CHECKING:
    from ..loaders.constants import ExternalAPI


def _build_fmp_price_params(query: QueryParams, symbol: str) -> dict[str, str]:
    """
    Map our inbound query parameters plus a single symbol onto FMP's query-param
    names for one external request.

    Kept pure (no environment or secret access) so it can be unit-tested in
    isolation. The API key is injected later, at the loader boundary.
    """

    return {
        "symbol": symbol,
        # FMP expects ISO date strings (YYYY-MM-DD).
        "from": query.start_date.isoformat(),
        "to": query.end_date.isoformat(),
    }


@dataclass(frozen=True)
class MetricCatalogEntry:
    """The data-source half of the lookup: everything needed to fetch a metric,
    independent of which analysis is applied to it."""

    external_api: ExternalAPI  # which loader / base URL to use, e.g. "FMP"
    endpoint: str  # external API path, no leading slash (base URL has the slash)
    build_params: Callable[[QueryParams, str], dict[str, str]]  # per-symbol params
    value_column: str  # the normalised column the transform recipe operates on
    merge_index: str = "date"  # identity column to sort/merge on


METRIC_CATALOG: dict[str, MetricCatalogEntry] = {
    "share-price": MetricCatalogEntry(
        external_api="FMP",
        # ⚠️ Cross-check against FMP stable docs: endpoint path and value column
        # names differ between /api/v3 and /stable.
        endpoint="historical-price-eod/full",
        build_params=_build_fmp_price_params,
        value_column="close",
    ),
}
