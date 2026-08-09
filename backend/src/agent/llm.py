from functools import cache
from inspect import cleandoc

from langchain.chat_models import init_chat_model
from langchain.messages import AIMessage
from langchain_core.language_models import LanguageModelInput
from langchain_core.runnables import Runnable

from ..dependencies import Environment, get_environment
from ..terminal.tools import TERMINAL_TOOLS

type ModelWithTools = Runnable[LanguageModelInput, AIMessage]


# System prompts tell the model about its role, how it should handle edge cases,
# and basic real-world context. Details on how to select and use tools can be
# found in their own docstrings and field descriptions

PLANNING_SYSTEM_PROMPT: str = cleandoc("""
Your should answer the user's question about finance, business, or economics
with a chart by making a single tool call.

- Call exactly one tool per turn.
- Derive every argument from the user's question and the tool's schema. Never
invent tickers, dates, or metric names to fill a required field.
- If no tool can answer the question or the question is too vague to fill the
required arguments, do not call a tool. Explain briefly in plain text what you
cannot do and what you would need to proceed.

All tools require an `analysis` argument. These so called "analysis functions"
are how you specify what data is displayed in charts. Think of them as sequential
operations on the columns of a spreadsheet. They are composable and should be
specified as nodes of a directed acyclic graph. Every node has two attributes:

- name: serves as this column's unique ID and display name. Duplicate names are
    not allowed.
- show: If true, it will be displayed in the output dataset and the chart as
    `name`, else it will be discarded at the end. At least one column must be
    shown.

Nodes also take custom arguments and their dependencies (fields that contain a
`Scope` enum in their metadata). Dependencies are referenced by name. Take care
not to produce cyclic references.

`Scope` describes the inputs and outputs of an analysis function. An entity is an
individual stock, commodity, etc.
- BASE: is used by BaseMetric to reference a base metric
- INDIVIDUAL: applies to a single entity
- COLLECTIVE: applies to all entities
- ANY: either INDIVIDUAL or COLLECTIVE

Dependencies referenced must match the `Scope` required by the field.

There are three types of analysis functions:

- Base metrics
    - Metrics readily available to a tool, giving one output column of
        `Scope.INDIVIDUAL` per entity.
    - To display one, you MUST specify a BaseMetric referencing it. For example,
        if you want to reference base metric `close`, make sure you add a
        BaseMetric with `metric="close"` and reference its name. You may set
        `show=False" 
    - Not supported by all tools, and the supported set varies (listed in the
        field description).

- Linear
    - Calculations involving a single entity that produce one output column per
        entity, e.g. percentage change, rolling average, normalise. This is of
        `Scope.COLLECTIVE` if all inputs resolve to `Scope.COLLECTIVE`, else
        `Scope.INDIVIDUAL`.
    - Supported by all tools, though the supported set varies.

- Aggregate
    - Calculations involving all individual entities that produce exactly one
        output column of `Scope.COLLECTIVE`, e.g. index to peer, rank, benchmark.
    - Not supported by all tools, and the supported set varies.
""")


@cache
def planning_node_llm() -> ModelWithTools:
    """Build an LLM client for the planning node."""

    env: Environment = get_environment()

    return init_chat_model(
        model=env.planning_node_model,
        model_provider=env.planning_node_provider,
        api_key=env.openrouter_api_key,
    ).bind_tools(TERMINAL_TOOLS)
