from collections.abc import Callable

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_tool_call
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langgraph.prebuilt import ToolRuntime
from langgraph.prebuilt.tool_node import ToolCallRequest

load_dotenv()


class NoSuchOrderException(Exception):
    def __init__(self, message: str):
        self.message = message


@tool
def fetch_order_status(order_id: str, runtime: ToolRuntime) -> str:
    """Fetch the order status for the given order_id."""
    raise NoSuchOrderException(f"Order #{order_id} not found!")


@wrap_tool_call
def handle_tool_errors(
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], ToolMessage]
) -> ToolMessage:
    """Convert tool exceptions into ToolMessages the model can handle."""
    try:
        return handler(request)
    except Exception as exc:
        return ToolMessage(
            content=f"Tool error: please check your input and try again. {exc}",
            tool_call_id=request.tool_call["id"]
        )


agent = create_agent(
    model="google_genai:gemini-3.1-flash-lite",
    tools=[fetch_order_status],
    middleware=[handle_tool_errors]
)
result = agent.invoke(
    {
        "messages": [{"role": "user", "content": "What is the status of order #12345?"}]
    }
)
messages = result["messages"]
for message in messages:
    print(message.content)
