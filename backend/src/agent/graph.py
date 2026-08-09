from functools import cache
from operator import add
from typing import Annotated, TypedDict

from langchain.messages import AIMessage, AnyMessage, ToolCall, ToolMessage
from langchain_core.tools import BaseTool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import tools_condition
from pydantic import ValidationError

from ..display.output_models import ChartConfigModel
from ..global_types import DataProcessingError, ImplementationError
from ..terminal.tools import TERMINAL_TOOLS_MAPPING
from .llm import planning_node_llm

# Keys of the AgentState TypedDict
MESSAGES: str = "messages"
CHART_CONFIG: str = "chart_config"


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add]  # Chat history, reduce by appending
    chart_config: ChartConfigModel


async def _planning_node(state: AgentState) -> dict:
    """LLM node that turns user's question into a tool call."""
    response: AIMessage = await planning_node_llm().ainvoke(state[MESSAGES])
    return {MESSAGES: [response]}


# Tool call TypedDict keys
TOOL_NAME: str = "name"
TOOL_ARGS: str = "args"
TOOL_ID: str = "id"


async def _tool_node(state: AgentState) -> dict:
    """Execute the tool the planning node called."""

    last_message: AnyMessage = state[MESSAGES][-1]

    if not isinstance(last_message, AIMessage) or not last_message.tool_calls:
        raise ValueError("Tool node reached without a pending tool call")

    if len(last_message.tool_calls) > 1:
        raise ValueError(f"Expected one tool call, got {len(last_message.tool_calls)}")

    tool_call: ToolCall = last_message.tool_calls[0]
    tool_selected: BaseTool = TERMINAL_TOOLS_MAPPING[tool_call[TOOL_NAME]]

    try:
        # Passing the arguments alone (not the whole call) returns the tool's
        # own value; passing the call would return a ToolMessage and discard
        # the objects we need.
        chart_config: ChartConfigModel = await tool_selected.ainvoke(
            tool_call[TOOL_ARGS]
        )
    except (DataProcessingError, ImplementationError, ValidationError) as e:
        return {
            MESSAGES: [
                ToolMessage(
                    content=f"{tool_call[TOOL_NAME]} failed: {e}",
                    tool_call_id=tool_call[TOOL_ID],
                )
            ]
        }

    return {
        MESSAGES: [
            ToolMessage(
                content=f"{tool_call[TOOL_NAME]} returned a chart: {chart_config.title.text}",
                tool_call_id=tool_call[TOOL_ID],
            )
        ],
        CHART_CONFIG: chart_config,
    }


# State graph nodes
PLANNING: str = "planning"
TOOLS: str = "tools"


@cache
def build_graph() -> CompiledStateGraph:
    """Build and compile the agent workflow graph."""

    graph: StateGraph = StateGraph(AgentState)

    graph.add_node(PLANNING, _planning_node)
    graph.add_node(TOOLS, _tool_node)

    graph.add_edge(START, PLANNING)
    graph.add_conditional_edges(PLANNING, tools_condition)
    graph.add_edge(TOOLS, END)

    return graph.compile()
