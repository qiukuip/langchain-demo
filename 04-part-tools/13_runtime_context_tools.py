from collections.abc import Callable

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import (
    ModelRequest,
    ModelResponse,
    wrap_model_call,
    wrap_tool_call,
)
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.prebuilt import ToolRuntime
from langgraph.prebuilt.tool_node import ToolCallRequest
from pydantic.dataclasses import dataclass

load_dotenv()


@dataclass
class Context:
    user_role: str = "viewer"


@tool
def query_order(order_id: str) -> str:
    """Query order information for a given order_id."""
    print(f"query order: #{order_id}")
    return f"Order #{order_id} is query successfully."


@tool
def edit_order(order_id: str) -> str:
    """Edit order information for a given order_id."""
    print(f"edit order: #{order_id}")
    return f"Order #{order_id} is edited successfully."


@tool
def delete_order(order_id: str, runtime: ToolRuntime) -> str:
    """Delete order information for a given order_id."""
    print(f"delete order: #{order_id}")
    user_role = runtime.context.user_role
    if user_role not in ("editor", "admin"):
        raise RuntimeError("Operation not permitted.")
    return f"Order #{order_id} is deleted successfully."


@wrap_model_call
def context_based_tools(
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
) -> ModelResponse:
    user_role = request.runtime.context.user_role
    print(f"user_role: {user_role}")
    tools = [query_order]
    if user_role == "editor":
        tools.append(edit_order)
        request = request.override(tools=tools)
    elif user_role == "admin":
        tools.extend([edit_order, delete_order])
        request = request.override(tools=tools)
    else:
        request = request.override(tools=tools)

    print("Tools sent to model: ", [t.name for t in request.tools])

    return handler(request)


@wrap_tool_call
def error_handling(
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], ToolMessage],
) -> ToolMessage:
    try:
        return handler(request)
    except Exception as e:
        return ToolMessage(
            content="Please check your input and try again.",
            tool_call_id=request.tool_call["id"]
        )


agent = create_agent(
    model="google_genai:gemini-3.1-flash-lite",
    tools=[query_order, edit_order, delete_order],
    middleware=[error_handling, context_based_tools],
)
result = agent.invoke(
    {"messages": [HumanMessage(content="delete order #12345 directly")], },
    context=Context(user_role="viewer"),
    config={"configurable": {"thread_id": "th-0413"}},
)
for message in result["messages"]:
    if message:
        print(message)
