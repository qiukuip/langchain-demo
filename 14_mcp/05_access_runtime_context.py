import asyncio
from dataclasses import dataclass

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.messages import HumanMessage, ToolMessage
from langchain_mcp_adapters.callbacks import (
    CallbackContext,
    LoggingMessageNotificationParams,
)
from langchain_mcp_adapters.client import Callbacks, MultiServerMCPClient
from langchain_mcp_adapters.interceptors import MCPToolCallRequest
from langgraph.types import Command


@dataclass
class CustomContext:
    user_id: str
    api_key: str


async def inject_user_context(request: MCPToolCallRequest, handler):
    """Inject user credentials into MCP tool calls"""
    runtime = request.runtime
    user_id = runtime.context.user_id
    api_key = runtime.context.api_key

    print(f"user_id: {user_id}")
    print(f"api_key: {api_key}")

    modified_request = request.override(
        args={**request.args, "user_id": user_id, "api_key": api_key}
    )
    return await handler(modified_request)


async def handle_task_completion(request: MCPToolCallRequest, handler):
    """Mark task complete and hand off to summary agent."""
    result = await handler(request)
    if request.name == "weather":
        return Command(
            update={
                "messages": [result] if isinstance(result, ToolMessage) else [],
                "task_status": "completed",
            }
        )
    return result


async def logging_interceptor(request: MCPToolCallRequest, handler):
    """Log tool call before and after execution"""
    print(f"Calling tool: {request.name} with args: {request.args}")
    result = await handler(request)
    print(f"Tool {request.name} returned: {result}")
    return result


async def auth_header_interceptor(request: MCPToolCallRequest, handler):
    """Add authentication headers based on the tool being called"""
    token = "my_token"
    print(f"Token: {token}")
    modified_request = request.override(headers={"Authorization": f"Bearer {token}"})
    return await handler(modified_request)


async def fallback_interceptor(request: MCPToolCallRequest, handler):
    """Return a fallback value if tool execution fails."""
    try:
        return await handler(request)
    except TimeoutError:
        return f"Tool {request.name} timed out. Please try again later."
    except ConnectionError:
        return f"Could not connect to {request.name} service. Using cached data."


async def on_progress(
    progress: float, total: float | None, message: str | None, context: CallbackContext
):
    """Handle progress updates from MCP servers."""
    percent = (progress / total * 100) if total else progress
    tool_info = f"({context.tool_name})" if context.tool_name else ""
    print(f"[{context.server_name}{tool_info}] Progress: {percent:.1f}% - {message}")


async def on_logging_message(
    params: LoggingMessageNotificationParams, context: CallbackContext
):
    """Handle log messages from MCP servers"""
    print(f"[{context.server_name}] {params.level}: {params.data}")


async def main():
    client = MultiServerMCPClient(
        {
            "weather": {
                "transport": "streamable_http",
                "url": "http://localhost:8000/mcp",
            }
        },
        tool_interceptors=[
            inject_user_context,
            logging_interceptor,
            auth_header_interceptor,
            fallback_interceptor,
        ],
        callbacks=Callbacks(
            on_progress=on_progress, on_logging_message=on_logging_message
        ),
    )
    tools = await client.get_tools()
    load_dotenv()
    agent = create_agent(
        model="google_genai:gemini-3.1-flash-lite",
        tools=tools,
        context_schema=CustomContext,
    )
    result = await agent.ainvoke(
        {"messages": [HumanMessage("Search weather condition in Chicago.")]},
        context=CustomContext(user_id="abc_123", api_key="sk-1234"),
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
