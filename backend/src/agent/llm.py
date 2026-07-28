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
Your job is to turn the user's question about finance, business, or economics
into a single tool call that will produce a chart that answers it.

- Call exactly one tool per turn.
- Derive every argument from the user's question and the tool's schema. Never
invent tickers, dates, or metric names to fill a required field.
- If no tool can answer the question or the question is too vague to fill the
required arguments, do not call a tool. Reply in plain text saying briefly
what you cannot do and what you would need to proceed.
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
