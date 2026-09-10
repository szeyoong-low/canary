from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict

from ..agent.router import invoke_agent
from ..display.output_models import ChartConfigModel

router = APIRouter(prefix="/agent")


class PromptObject(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str


@router.post("/")
async def ask_agent_handler(prompt_object: PromptObject) -> ChartConfigModel:
    return (await invoke_agent(prompt_object.text))["chart"]
