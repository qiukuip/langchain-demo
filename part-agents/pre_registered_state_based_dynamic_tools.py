from typing import Callable

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import ModelRequest, ModelResponse, wrap_model_call
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

from my_state import MyState

load_dotenv(verbose=True)


@tool
def public_search(query: str) -> str:
    """适用于普通用户或未登录状态，获取基础的、公开可查的用户信息。参数 query 是姓名。"""
    print("Public Searching")
    return f"Result of public search of {query}."


@tool
def private_search(query: str) -> str:
    """仅限已授权用户。获取内部或隐私级别较高的用户详细数据。参数 query 是姓名。"""
    print("Private Searching")
    return f"Result of private search of {query}."


@tool
def advanced_search(query: str) -> str:
    """获取高级用户信息。参数 query 是姓名。"""
    print("Advanced Searching")
    return f"Result of advanced search of {query}."


@wrap_model_call
def state_based_tools(
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse]
) -> ModelResponse:
    """基于对话状态过滤工具"""
    state = request.state or {}
    print("state: ", state)
    is_authenticated = state.get("authenticated", False)
    message_count = len(request.messages)

    print("is_authenticated: ", is_authenticated)
    print("message_count: ", message_count)

    current_tools = request.tools
    if not is_authenticated:
        current_tools = [t for t in request.tools if t.name.startswith("public_")]
    elif message_count < 5:
        current_tools = [t for t in request.tools if t.name != "advanced_search"]
    print("current_tools: ", current_tools)

    request = request.override(tools=current_tools)

    return handler(request)


agent = create_agent(
    model=ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite"),
    tools=[public_search, private_search, advanced_search],
    middleware=[state_based_tools],
    state_schema=MyState
)
result = agent.invoke(
    {"messages": [{"role": "user", "content": "帮我查询用户“张三”的信息。"}]},
    state=MyState(authenticated=True)
)
print(result["messages"][-1].content)
