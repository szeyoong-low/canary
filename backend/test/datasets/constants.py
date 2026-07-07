from pathlib import Path
from typing import Literal

JSON_EXT: str = ".json"

type Dataset = Literal["fmp_prod_segment_raw", "fmp_prod_segment_norm"]


def dataset_path(dataset: Dataset) -> str:
    return f"{Path(__file__).parent}/{dataset}{JSON_EXT}"
