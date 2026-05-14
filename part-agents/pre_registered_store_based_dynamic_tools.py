from typing import Callable

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import ModelRequest, ModelResponse, wrap_model_call
from langchain_core.stores import InMemoryStore
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

from context import Context

load_dotenv(verbose=True)


@tool
def search_tool() -> str:
    """查询信息。"""
    print("running search tool")
    return f"Result of search tool."


@tool
def analysis_tool() -> str:
    """分析信息。"""
    print("running analysis tool")
    return f"Result of analysis tool."


@tool
def export_tool() -> str:
    """导出信息"""
    print("running export tool")
    return f"Result of export tool."


@wrap_model_call
def store_based_tools(
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse]
) -> ModelResponse:
    """基于存储的信息过滤工具"""
    user_id = request.runtime.context.get("user_id")
    store = request.runtime.store
    feature_flags = store.mget([user_id])
    if len(feature_flags) > 0:
        tools = [t for t in request.tools if t.name in feature_flags]
        request = request.override(tools=tools)

    return handler(request)


store = InMemoryStore()
store.mset([("u02", "search_tool")])
agent = create_agent(
    model=ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite"),
    tools=[search_tool, analysis_tool, export_tool],
    middleware=[store_based_tools],
    context_schema=Context,
    store=store
)
result = agent.invoke(
    {"messages": [{"role": "user", "content": "处理信息"}]},
    context=Context(user_id="u02", user_role="")
)
print(result["messages"][-1].content)
