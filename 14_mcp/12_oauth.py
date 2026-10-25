"""使用 OAuth 调用本地 MCP 服务，无需手动填写 Bearer Token。

在仓库根目录的两个终端中分别运行：
    python 14_mcp/servers/oauth_server.py
    python 14_mcp/12_oauth.py

客户端自动打开浏览器；输入 alice / demo-password，点击“登录并同意授权”。
服务随后将授权码回调到客户端本地临时端口；点击拒绝则终止授权。
令牌默认保存在内存中，每次重新运行客户端都会重新授权。
"""

import asyncio

from fastmcp import Client
from fastmcp.client import OAuth
from langchain.mcp import MCPAdapter

OAUTH_MCP_URL = "http://localhost:8002/mcp"


async def load_tools_with_oauth(url: str) -> list:
    # 自动完成服务发现、动态客户端注册、授权码 + PKCE 和令牌交换。
    # 后续请求由客户端自动添加 Authorization: Bearer <access_token>。
    oauth = OAuth(
        mcp_url=url,
        scopes=["demo:read"],
        client_name="LangChain OAuth Demo",
    )
    client = Client(url, auth=oauth)
    async with MCPAdapter(client) as adapter:
        return await adapter.list_tools()


async def main():
    print("即将打开浏览器，请使用 alice / demo-password 登录并确认授权。")
    tools = await load_tools_with_oauth(OAUTH_MCP_URL)
    for tool in tools:
        print(f"Found tool: {tool.name}")
        print(f"\t{tool.description}")

    # 适配后的工具保留 OAuth 客户端，调用时继续使用已获取的令牌。
    auth_tool = next(tool for tool in tools if tool.name == "get_auth_info")
    result = await auth_tool.ainvoke({})
    print(f"Auth info: {result}")


if __name__ == "__main__":
    asyncio.run(main())
