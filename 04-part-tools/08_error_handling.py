from typing import Callable

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_tool_call
from langchain.tools.tool_node import ToolCallRequest
from langchain_core.messages import ToolMessage


load_dotenv()


@wrap_tool_call
def handle_tool_errors(
    request: ToolCallRequest, handler: Callable[[ToolCallRequest], ToolMessage]
) -> ToolMessage:
    """Convert tool exception into ToolMessage the model can handle"""
    try:
        return handler(request)
    except Exception as e:
        return ToolMessage(
            content=f"工具调用错误，请重试。({str(e)})",
            tool_call_id=request.tool_call["id"],
        )


agent = create_agent(
    model="google_genai:gemini-3.1-flash-lite",
    tools=[],
    middleware=[handle_tool_errors],
)
response = agent.invoke({"messages": [{"role": "user", "content": "光子从何而来？"}]})
print(response)
