from typing import cast

from fastapi import APIRouter, HTTPException
from httpx import codes
from langchain.messages import AnyMessage, HumanMessage, SystemMessage

from ..display.output_models import ChartConfigModel
from .graph import build_graph, CHART_CONFIG, MESSAGES, AgentState
from .input_models import Prompt
from .llm import PLANNING_SYSTEM_PROMPT

router = APIRouter(prefix="/agent")


# POST over GET (https://blog.postman.com/get-vs-post/#how-to-choose-between-get-and-post):
# 1. GET requests are meant to pass data in the URLs which have practical length
#    limits, making them unsuitable for highly detailed questions. It is better
#    to pass the prompt in the request body. Also, prompts may contain sensitive
#    details (e.g. frequently mentioned securities may give away an investor's
#    positions).
# 2. GET is meant to be a safe, idempotent resource retrieval. Prompts to AI
#    agents are neither "safe" nor idempotent (each call may cost money, hit
#    rate limits, or produce a different result). POST is meant for submitting
#    data to be processed.
# 3. Since charts will be saved to a user's account, the request changes server
#    state.


@router.post("/")
async def ask_agent_handler(prompt: Prompt) -> ChartConfigModel:
    """Answer a natural language question (in request body) with a chart."""

    final_state: AgentState = cast(
        AgentState,
        await build_graph().ainvoke(
            {
                MESSAGES: [
                    SystemMessage(PLANNING_SYSTEM_PROMPT),
                    HumanMessage(prompt.text),
                ]
            }
        ),
    )
    chart_config: ChartConfigModel | None = final_state.get(CHART_CONFIG)

    if chart_config is None:
        # The model either declined to call a tool (AIMessage is last message)
        # or the tool failed (ToolMessage is the last message)
        last_message: AnyMessage = final_state[MESSAGES][-1]
        raise HTTPException(codes.UNPROCESSABLE_ENTITY, last_message.text)

    return chart_config
