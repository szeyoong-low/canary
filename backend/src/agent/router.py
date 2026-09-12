from typing import cast

from fastapi import HTTPException
from httpx import codes
from langchain.messages import AnyMessage, HumanMessage, SystemMessage

from ..terminal.utility import TerminalToolResult
from .graph import MESSAGES, TERMINAL_TOOL_RESULT, AgentState, build_graph
from .llm import PLANNING_SYSTEM_PROMPT


async def invoke_agent(prompt: str) -> TerminalToolResult:
    """Answer a natural language question (in request body) with a chart."""

    final_state: AgentState = cast(
        AgentState,
        await build_graph().ainvoke(
            {
                MESSAGES: [
                    SystemMessage(PLANNING_SYSTEM_PROMPT),
                    HumanMessage(prompt),
                ]
            }
        ),
    )
    result: TerminalToolResult | None = final_state.get(TERMINAL_TOOL_RESULT)

    if result is None:
        # The model either declined to call a tool (AIMessage is last message)
        # or the tool failed (ToolMessage is the last message)
        last_message: AnyMessage = final_state[MESSAGES][-1]
        raise HTTPException(codes.UNPROCESSABLE_ENTITY, last_message.text)

    return result
