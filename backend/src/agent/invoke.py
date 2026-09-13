from typing import cast

from fastapi import HTTPException, status
from langchain.messages import AnyMessage, HumanMessage

from ..terminal.utility import TerminalToolResult
from .graph import (
    MESSAGES,
    TERMINAL_TOOL_FAILURE,
    TERMINAL_TOOL_RESULT,
    AgentState,
    ToolFailure,
    build_graph,
)
from .llm import PLANNING_SYSTEM_MESSAGE

# Mask internal failures
FAILURE_MESSAGE: str = (
    "There were difficulties processing your request. Please try again."
)


async def invoke_agent(prompt: str) -> TerminalToolResult:
    """Answer a natural language question (in request body) with a chart."""

    final_state: AgentState = cast(
        AgentState,
        await build_graph().ainvoke(
            {
                MESSAGES: [
                    PLANNING_SYSTEM_MESSAGE,
                    HumanMessage(prompt),
                ]
            }
        ),
    )
    result: TerminalToolResult | None = final_state.get(TERMINAL_TOOL_RESULT)

    if result is not None:
        return result

    failure: ToolFailure | None = final_state.get(TERMINAL_TOOL_FAILURE)

    if failure is None:
        # Tool node never ran, planning node declined to call a tool and said
        # why in plain text. Help user to re-prompt
        last_message: AnyMessage = final_state[MESSAGES][-1]
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, last_message.text)

    raise HTTPException(
        status.HTTP_500_INTERNAL_SERVER_ERROR
        if failure is ToolFailure.FATAL
        else status.HTTP_422_UNPROCESSABLE_CONTENT,
        FAILURE_MESSAGE,
    )
