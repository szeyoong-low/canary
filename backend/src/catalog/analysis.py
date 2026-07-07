from dataclasses import dataclass


@dataclass(frozen=True)
class AnalysisCatalogEntry:
    pass


ANALYSIS_CATALOG: dict[str, AnalysisCatalogEntry] = {}
