from dataclasses import dataclass


@dataclass(frozen=True)
class MetricCatalogEntry:
    pass


METRIC_CATALOG: dict[str, MetricCatalogEntry] = {}
