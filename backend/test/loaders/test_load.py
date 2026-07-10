from json import load
from typing import Any
from unittest.mock import AsyncMock, Mock, patch

from httpx import codes
from polars import DataFrame, read_json
from polars.testing import assert_frame_equal

from .constants import FMP_API, BASE_URL_DISPATCH, NORMALISER_DISPATCH
from ..datasets.paths import dataset_path
from src.loaders.load import load_data


# Internally-constructed dependencies are patched
@patch.dict(BASE_URL_DISPATCH, {FMP_API: (lambda: "")})
@patch.dict(NORMALISER_DISPATCH, {FMP_API: lambda x: x})
async def test_load_only_regular():
    """Loading a non-edge case without normalisation should return the original JSON"""
    data_file: str = dataset_path("fmp_prod_segment_raw")
    with open(data_file, mode="r") as data:
        original_json: Any = load(data)

    # Injected dependencies are mocked
    response: Mock = Mock(status_code=codes.OK, **{"json.return_value": original_json})
    http_client: Mock = Mock(get=AsyncMock(return_value=response))

    actual: DataFrame = (
        await load_data(http_client, FMP_API, "TEST", {}, {})
    ).collect()
    expected: DataFrame = read_json(data_file)
    assert_frame_equal(actual, expected)
