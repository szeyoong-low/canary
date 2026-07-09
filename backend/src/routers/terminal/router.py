from typing import Annotated

from fastapi import APIRouter, Query
from pydantic import BaseModel, ConfigDict


TERMINAL_PREFIX = "/terminal"
router = APIRouter(prefix=TERMINAL_PREFIX)

# Path parameters
METRIC_PATH_PARAM = "/{metric}"
DISPLAY_PATH_PARAM = "/{display}"
TERMINAL_PATH = f"{METRIC_PATH_PARAM}{DISPLAY_PATH_PARAM}"


class PathHandlerModel(BaseModel):
    """Query parameters that must be present for all requests"""

    # The raw query parameters will be passed to transformations to be parsed
    # independently with their own Pydantic models.
    model_config = ConfigDict(extra="ignore")

    analysis: list[str]
    view: list[str]
    symbol: list[str]


@router.get(TERMINAL_PATH)
def terminal_path_op(
    metric: str, display: str, query: Annotated[PathHandlerModel, Query()]
):
    return {"metric": metric, "display": display, **query.model_dump()}
