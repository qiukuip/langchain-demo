from typing import Callable

from langchain.agents.middleware import (
    ModelRequest,
    ModelResponse,
    wrap_model_call,
    wrap_tool_call,
)
from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage, ToolMessage
from langchain.tools.tool_node import ToolCallRequest
from langgraph.types import Command


@wrap_model_call
def add_context(
    request: ModelRequest, handler: Callable[[ModelRequest], ModelResponse]
) -> ModelResponse:
    new_content = list(request.system_message.content_blocks) + [
        {"type": "text", "text": "Additional text"}
    ]
    new_system_message = SystemMessage(content=str(new_content))
    return handler(request.override(system_message=new_system_message))


base_model = init_chat_model(
    model="gemini-2.5-flash-lite", model_provider="google_genai", temperature=0.8
)
advanced_model = init_chat_model(
    model="gemini-3.1-flash-lite", model_provider="google_genai", temperature=0.8
)


@wrap_model_call
def dynamic_model(
    request: ModelRequest, handler: Callable[[ModelRequest], ModelResponse]
) -> ModelResponse:
    model = base_model
    if len(request.messages) > 10:
        model = advanced_model
    return handler(request.override(model=model))


@wrap_model_call
def select_tools(
    request: ModelRequest, handler: Callable[[ModelRequest], ModelResponse]
) -> ModelResponse:
    tools = request.tools
    for tool in tools:
        print(f"Tool name: {tool.name}")
    relevant_tools = [t for t in tools if t.name != "unuse_tool"]
    return handler(request.override(tools=relevant_tools))


@wrap_tool_call
def monitor_tool(
    request: ToolCallRequest,
    handler: Callable[[ToolCallRequest], ToolMessage | Command],
) -> ToolMessage | Command:
    print(f"Executing tool: {request.tool_call['name']}")
    print(f"Arguments: {request.tool_call['args']}")
    try:
        result = handler(request)
        print("Tool completed successfully")
        return result
    except Exception as e:
        print(f"Tool failed: {e}")
        raise
