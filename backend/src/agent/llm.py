from langchain.chat_models import BaseChatModel, init_chat_model

from ..dependencies import Environment


def planning_node_llm(env: Environment) -> BaseChatModel:
    """Build an LLM client for the planner node."""

    return init_chat_model(
        model=env.planning_node_model,
        model_provider=env.planning_node_provider,
        api_key=env.openrouter_api_key,
    )
