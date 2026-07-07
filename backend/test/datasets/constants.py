from pathlib import Path
from typing import Callable, Literal

JSON_EXT: str = ".json"

type Dataset = Literal["fmp_prod_segment_raw", "fmp_prod_segment_norm"]


dataset_path: Callable[[Dataset], str] = lambda dataset: (
    f"{Path(__file__).parent}/{dataset}{JSON_EXT}"
)
