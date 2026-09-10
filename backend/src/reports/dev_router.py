from fastapi import APIRouter

from ..agent.router import invoke_agent
from ..display.output_models import ChartConfigModel
from .types import PromptBody

router = APIRouter(prefix="/dev/agent")


@router.post("/")
async def agent_smoke_test(prompt_body: PromptBody) -> ChartConfigModel:
    return (await invoke_agent(prompt_body.prompt))["chart"]
