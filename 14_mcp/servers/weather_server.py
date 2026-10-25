import os

from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.server.auth import StaticTokenVerifier

load_dotenv()

tokens = {
    "token-for-client1": {
        "client_id": "client1",
        "scope": ["weather:read"]
    }
}

# FastMCP 在收到 HTTP 请求时校验 Authorization: Bearer <token>。
# 缺失或错误令牌返回 401；未配置允许的令牌时，服务仍启动但拒绝所有请求。
auth = StaticTokenVerifier(
    tokens=tokens
)

mcp = FastMCP("Weather", auth=auth)

tags = {"weather", "demo"}
tool_metadata = {
    "category": "weather",
    "version": "1.0",
    "source": "mock",
}


@mcp.tool(
    tags=tags,
    # 自定义元数据通过 MCP 的 _meta 字段传递给客户端。
    meta=tool_metadata,
    annotations={
        "readOnlyHint": True,
        "destructiveHint": True,
    },
)
async def get_weather(location: str) -> str:
    """Get weather for a location."""
    if location == "New York":
        return "It's sunny in New York"
    elif location == "Chicago":
        return "It's cloudy in Chicago"
    elif location == "Los Angeles":
        return "It's sunny in Los Angeles"
    elif location == "San Francisco":
        return "It's foggy in San Francisco"
    else:
        raise Exception(f"Unknown location: {location}")


if __name__ == "__main__":
    mcp.run(transport="streamable-http", port=8001)
