from fastmcp.client import Client
from fastmcp.client.auth import BearerAuth
from langchain.agents import create_agent
from langchain.mcp import MCPAdapter

CONFIG = {
    "mcpServers": {
        "docs": {"url": "https://example.com/mcp"}
    }
}


def token_for_user(user: str) -> str:
    return user


async def make_graph(runtime):
    user = runtime.user.identity if runtime.user is not None else "anonymous"
    auth = BearerAuth(token=token_for_user(user))
    async with MCPAdapter(Client(CONFIG, auth=auth)) as adapter:
        tools = await adapter.list_tools()
        return create_agent("claude-sonnet-5", tools)
