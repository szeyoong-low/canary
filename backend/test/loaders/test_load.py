from json import load
from typing import Any
from unittest.mock import AsyncMock, Mock, patch

from httpx import codes
from polars import DataFrame, read_json
from polars.testing import assert_frame_equal

from . import constants as const
from ..datasets import dataset_path
from src.loaders import load_data


# Internally-constructed dependencies are patched
@patch.dict(const.BASE_URL_DISPATCH, {const.FMP_API: (lambda: "")})
@patch.dict(
    const.NORMALISER_DISPATCH,
    {const.FMP_API: lambda x: x},
)
async def test_load_only_regular():
    """Loading a non-edge case without normalisation should return the original JSON"""
    data_file: str = dataset_path("fmp_prod_segment_raw")
    with open(data_file, mode="r") as data:
        original_json: Any = load(data)

    # Injected dependencies are mocked
    response: Mock = Mock(status_code=codes.OK, **{"json.return_value": original_json})
    http_client: Mock = Mock(get=AsyncMock(return_value=response))

    actual: DataFrame = (
        await load_data(http_client, const.FMP_API, "TEST", {}, {})
    ).collect()
    expected: DataFrame = read_json(data_file)
    assert_frame_equal(actual, expected)
