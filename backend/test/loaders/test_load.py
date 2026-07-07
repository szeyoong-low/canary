from json import load
from unittest.mock import AsyncMock, Mock, patch
from typing import Any

from httpx import codes
from polars import DataFrame, read_json
from polars.testing import assert_frame_equal

from datasets import dataset_path
from src.loaders import constants, load_data

LOADERS_CONSTANTS_PATH: str = "src.loaders.constants."
BASE_URL_DISPATCH: str = "BASE_URL"
NORMALISER_DISPATCH: str = "NORMALISER"
DUMMY_STRING: str = ""
FMP_API: constants.ExternalAPI = "FMP"


# Internally-constructed dependencies are patched
@patch.dict(f"{LOADERS_CONSTANTS_PATH}{BASE_URL_DISPATCH}", {FMP_API: (lambda: DUMMY_STRING)})
@patch.dict(f"{LOADERS_CONSTANTS_PATH}{NORMALISER_DISPATCH}", {FMP_API: lambda x: x})
async def test_load_regular():
    """Loading without normalisation should return the original JSON"""
    dataset_file: str = dataset_path("fmp_wide")
    with open(dataset_file, mode="r") as data:
        original_json: Any = load(data)
        
    # Injected dependencies are mocked
    response: Mock = Mock(status_code=codes.OK, **{"json.return_value": original_json})
    http_client: Mock = Mock(get=AsyncMock(return_value=response))

    actual: DataFrame = (await load_data(http_client, FMP_API, DUMMY_STRING, {})).collect()
    expected: DataFrame = read_json(dataset_file)
    assert_frame_equal(actual, expected)
