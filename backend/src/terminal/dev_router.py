from typing import Annotated, Any

from fastapi import APIRouter, Body

from ..display.output_models import ChartConfigModel
from .tools import TERMINAL_TOOLS_MAPPING

router = APIRouter(prefix="/dev/terminal")


@router.post("/{tool_name}")
async def terminal_smoke_test(
    tool_name: str, args: Annotated[Any, Body()]
) -> ChartConfigModel:
    return (await TERMINAL_TOOLS_MAPPING[tool_name].ainvoke(args))["chart"]
