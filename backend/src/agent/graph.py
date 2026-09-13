from enum import StrEnum
from functools import cache
from operator import add
from typing import Annotated, TypedDict

from langchain.messages import AIMessage, AnyMessage, ToolCall, ToolMessage
from langchain_core.tools import BaseTool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import tools_condition
from pydantic import ValidationError

from ..global_types import DataProcessingError, ImplementationError
from ..observability.telemetry import log
from ..terminal.tools import TERMINAL_TOOLS_MAPPING, TerminalToolResult
from .llm import planning_node_llm


class ToolFailure(StrEnum):
    """Why the tool node produced no chart"""

    RECOVERABLE = "recoverable"  # Bad arguments, no data for them, or bad shape
    FATAL = "fatal"  # A bug on our side


# How many times the tool node may run for one question. Two means the model
# gets exactly one correction, which is the point of diminishing returns.
# LangGraph's own `recursion_limit` is only a crash-stop backstop.
MAX_TOOL_ATTEMPTS: int = 2

# Keys of the AgentState TypedDict
MESSAGES: str = "messages"
TERMINAL_TOOL_RESULT: str = "terminal_tool_result"
TERMINAL_TOOL_FAILURE: str = "terminal_tool_failure"
TOOL_ATTEMPTS: str = "tool_attempts"


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add]  # Chat history, reduce by appending
    terminal_tool_result: TerminalToolResult
    # Written on every tool node run, `None` on success, so that a failure from
    # an earlier attempt cannot linger.
    # Absent entirely only when the tool node never ran at all.
    terminal_tool_failure: ToolFailure | None
    # Counts tool node runs. It lives in state, not in a module-level variable,
    # because nodes must be pure functions of state. A shared counter would
    # bleed across concurrent requests.
    tool_attempts: int


async def _planning_node(state: AgentState) -> dict:
    """LLM node that turns user's question into a tool call."""
    response: AIMessage = await planning_node_llm().ainvoke(state[MESSAGES])
    return {MESSAGES: [response]}


# Tool call TypedDict keys
TOOL_NAME: str = "name"
TOOL_ARGS: str = "args"
TOOL_ID: str = "id"

_ONE_TOOL_ONLY: str = (
    "Expected exactly one tool call, got {count}. Retry with a single tool call "
    "that answers the whole question."
)


async def _tool_node(state: AgentState) -> dict:
    """Execute the tool the planning node called."""

    attempts: int = state.get(TOOL_ATTEMPTS, 0) + 1
    last_message: AnyMessage = state[MESSAGES][-1]

    if not isinstance(last_message, AIMessage) or not last_message.tool_calls:
        # Unreachable unless the graph is miswired, since `tools_condition` only
        # routes here when tool calls are pending. Reported rather than raised
        # so that a wiring bug still leaves through the same generic reply as
        # any other bug, instead of a traceback.
        log("ERROR", "agent.tool_node_without_call", message_type=type(last_message))
        return {TERMINAL_TOOL_FAILURE: ToolFailure.FATAL, TOOL_ATTEMPTS: attempts}

    if len(last_message.tool_calls) > 1:
        count: int = len(last_message.tool_calls)
        log("WARNING", "agent.multiple_tool_calls", count=count)

        return {
            # OpenAI-compatible APIs reject the next request if an AIMessage
            # with N tool calls isn't followed by N `ToolMessages`
            MESSAGES: [
                ToolMessage(
                    content=_ONE_TOOL_ONLY.format(count=count),
                    tool_call_id=call[TOOL_ID],
                )
                for call in last_message.tool_calls
            ],
            TERMINAL_TOOL_FAILURE: ToolFailure.RECOVERABLE,
            TOOL_ATTEMPTS: attempts,
        }

    tool_call: ToolCall = last_message.tool_calls[0]
    tool_selected: BaseTool = TERMINAL_TOOLS_MAPPING[tool_call[TOOL_NAME]]

    try:
        # Passing the arguments alone (not the whole call) returns the tool's
        # own value; passing the call would return a ToolMessage and discard
        # the objects we need.
        result: TerminalToolResult = await tool_selected.ainvoke(tool_call[TOOL_ARGS])
    except (DataProcessingError, ValidationError, ImplementationError) as e:
        fatal: bool = isinstance(e, ImplementationError)

        log(
            "ERROR" if fatal else "WARNING",
            "agent.tool_failed",
            error=e,
            tool=tool_call[TOOL_NAME],
            arguments=tool_call[TOOL_ARGS],
            # Identifies which raise site fired, which the message alone may not.
            code=e.code if fatal else None,
        )

        return {
            # The full text goes to the model, not to the user
            MESSAGES: [
                ToolMessage(
                    content=f"{tool_call[TOOL_NAME]} failed: {e}",
                    tool_call_id=tool_call[TOOL_ID],
                )
            ],
            TERMINAL_TOOL_FAILURE: (
                ToolFailure.FATAL if fatal else ToolFailure.RECOVERABLE
            ),
            TOOL_ATTEMPTS: attempts,
        }

    return {
        MESSAGES: [
            ToolMessage(
                content=f"{tool_call[TOOL_NAME]} returned a chart: {result['chart'].title.text}",
                tool_call_id=tool_call[TOOL_ID],
            )
        ],
        TERMINAL_TOOL_RESULT: result,
        TERMINAL_TOOL_FAILURE: None,
        TOOL_ATTEMPTS: attempts,
    }


# State graph nodes
PLANNING: str = "planning"
TOOLS: str = "tools"


def _after_tool_node(state: AgentState) -> str:
    """Send a recoverable failure back for one more try but end on anything else."""

    if state.get(TERMINAL_TOOL_RESULT) is not None:
        return END

    if (
        state.get(TERMINAL_TOOL_FAILURE) is ToolFailure.RECOVERABLE
        and state[TOOL_ATTEMPTS] < MAX_TOOL_ATTEMPTS
    ):
        # The planning node re-reads the whole history, so the ToolMessage the
        # failure just appended is the correction it works from.
        return PLANNING

    return END


@cache
def build_graph() -> CompiledStateGraph:
    """Build and compile the agent workflow graph."""

    graph: StateGraph = StateGraph(AgentState)

    graph.add_node(PLANNING, _planning_node)
    graph.add_node(TOOLS, _tool_node)

    graph.add_edge(START, PLANNING)
    graph.add_conditional_edges(PLANNING, tools_condition)
    graph.add_conditional_edges(TOOLS, _after_tool_node, [PLANNING, END])

    return graph.compile()
