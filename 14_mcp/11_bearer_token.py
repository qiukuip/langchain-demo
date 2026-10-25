import asyncio

from dotenv import load_dotenv
from fastmcp.client import Client
from langchain.mcp import MCPAdapter

load_dotenv()

WEATHER_MCP_URL = "http://localhost:8001/mcp"


async def load_tools_with_bearer(url: str, token: str) -> list:
    # 传入原始令牌，Client 自动添加 Authorization: Bearer <token> 请求头。
    async with MCPAdapter(Client(url, auth=token)) as adapter:
        return await adapter.list_tools()


async def main():
    token = "token-for-client1"
    if not token:
        raise ValueError("请设置 WEATHER_MCP_TOKEN")

    tools = await load_tools_with_bearer(WEATHER_MCP_URL, token)
    for tool in tools:
        print(f"Found tool: {tool.name}")
        print(f"\t{tool.description}")

    weather_tool = next(tool for tool in tools if tool.name == "get_weather")
    result = await weather_tool.ainvoke({"location": "San Francisco"})
    print(f"Weather: {result}")


if __name__ == "__main__":
    asyncio.run(main())
