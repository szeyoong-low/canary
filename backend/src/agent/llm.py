from functools import lru_cache
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
Your should turn the user's question about finance, business, or economics
into a single tool call that produces a chart that answers it.

- Call exactly one tool per turn.
- Derive every argument from the user's question and the tool's schema. Never
invent tickers, dates, or metric names to fill a required field.
- If no tool can answer the question or the question is too vague to fill the
required arguments, do not call a tool. Reply in plain text saying briefly
what you cannot do and what you would need to proceed.

All tools require an `analysis` argument. These so called "analysis functions"
are how you specify what data is displayed in charts. They are series of composed
transformations that operate on:

- **Individual entities:** base metrics or calculations involving a single entity,
e.g. percentage change, rolling average, normalise (all tools accept these)
- **Aggregate (all entities):** calculations involving all individual entities,
e.g. index to peer, rank, benchmark (not all tools accept these)

An entity is an individual stock, commodity, etc.
For now, aggregate transformations cannot be composed further.

Specify each analysis function as `<foo>/<bar>/<baz>`, where `bar` is applied on
`foo` and `baz` is applied on `bar`. Each transformation depends on its immediate
precedecessor, which is the suffix.

The first of these must be a base metric (something directly obtainable from data
without any calculations) or an individual transformation with no dependencies.
An analysis function must always be provided, even if it is to select a base metric for viewing.

Examples:
- Simply select for viewing, with no transformation
    - `vwap`
- Apply one transformation
    - `vwap/returns`
    - `bid,ask/spread`: requires `bid` and `ask`, one transformation (non-commutative)
- Applies two composed transformations
    - `vwap/returns/normalise`
    - `vwap/returns/realised-volatility`
- Applies three composed transformations
    - `vwap/returns/realised-volatility/normalise` 

If the first transformation is a list (e.g. `bid,ask/spread`), the next
transformation must take this number of arguments and fuse them into a single metric.

Aggregate transformations must come after individual transformations.
- `vwap/returns/rank`: Always depends on an individual transformation or base metric.
""")


@lru_cache
def planning_node_llm() -> ModelWithTools:
    """Build an LLM client for the planning node."""

    env: Environment = get_environment()

    return init_chat_model(
        model=env.planning_node_model,
        model_provider=env.planning_node_provider,
        api_key=env.openrouter_api_key,
    ).bind_tools(TERMINAL_TOOLS)
