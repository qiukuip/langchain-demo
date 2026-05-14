from typing import Callable

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_tool_call, ModelRequest
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv(verbose=True)


@tool
def search() -> str:
    """用于查询黑名单信息。"""
    return f"Results for query."


@tool
def get_weather(location: str) -> str:
    """获取某个地方的气温。"""
    return f"Weather in {location}: sunny, 72ºF."


@tool
def custom_multiply(a: int, b: int) -> int:
    """计算两个整数的自定义乘积。"""
    return a * b + 100


@wrap_tool_call
def handle_tool_errors(
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelRequest]
):
    """使用自定义错误消息处理工具调用错误。"""
    try:
        return handler(request)
    except Exception as e:
        return ToolMessage(content=f"工具调用错误，请重试。({str(e)})", tool_call_id=request.tool_call_id["id"])


model = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")
agent = create_agent(
    model=model,
    tools=[search, get_weather, custom_multiply]
)
messages = [
    {"role": "user", "content": "洛杉矶的气温"},
    {"role": "user", "content": "查询黑名单信息"},
    {"role": "user", "content": "计算一下 2 和 3 的自定义乘积。"}
]
result = agent.invoke({"messages": messages})
print(result)
