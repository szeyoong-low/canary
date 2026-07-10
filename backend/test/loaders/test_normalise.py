from json import load
from typing import Any
from unittest.mock import AsyncMock, Mock, patch

from httpx import codes
from polars import DataFrame, read_json
from polars.testing import assert_frame_equal

from .constants import BASE_URL_DISPATCH, FMP_API
from ..datasets.paths import dataset_path
from src.loaders.load import load_data


@patch.dict(BASE_URL_DISPATCH, {FMP_API: (lambda: "")})
async def test_normalise_nested():
    """A dataset with nested JSON objects is normalised to a wide dataset"""
    input_file: str = dataset_path("fmp_prod_segment_raw")
    with open(input_file, mode="r") as data:
        input_json: Any = load(data)

    response: Mock = Mock(status_code=codes.OK, **{"json.return_value": input_json})
    http_client: Mock = Mock(get=AsyncMock(return_value=response))

    actual: DataFrame = (
        await load_data(http_client, FMP_API, "TEST", {}, {})
    ).collect()

    output_file: str = dataset_path("fmp_prod_segment_norm")
    expected: DataFrame = read_json(output_file)
    assert_frame_equal(actual, expected)
