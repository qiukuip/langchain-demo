from typing import Callable

from dotenv import load_dotenv
from langchain.agents.middleware import wrap_model_call, ModelResponse, ModelRequest
from langgraph.prebuilt.tool_node import ToolCallRequest

load_dotenv()


@wrap_model_call
def state_based_tools(
        request: ModelRequest,
        handler: Callable[[ToolCallRequest], ModelResponse],
) -> ModelResponse:
    """Filter tools based on conversation state."""
    state = request.state
    is_authenticated: bool = state.is_authenticated
    message_count = len(state.messages)
    if not is_authenticated:
        tools = [tool for tool in state.tools if tool.name.startswith("public")]
        request.override(tools=tools)
    elif message_count < 5:
        tools = [tool for tool in state.tools if tool.name != "advanced_search"]
        request.override(tools=tools)

    return handler(request)
