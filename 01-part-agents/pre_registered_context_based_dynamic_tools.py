from typing import Callable

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

from context import Context

load_dotenv(verbose=True)


@wrap_model_call
def context_based_tools(request: ModelRequest, handler: Callable[[ModelRequest], ModelResponse]) -> ModelResponse:
    if request.runtime is None or request.runtime.context is None:
        user_role = "viewer"
    else:
        user_role = request.runtime.context.get("user_role", "viewer")
    print("user role: ", user_role)

    current_tools = request.tools
    if user_role == "admin":
        pass
    elif user_role == "editor":
        current_tools = [t for t in request.tools if t.name != "delete_data"]
    else:
        current_tools = [t for t in request.tools if t.name.startswith("read_")]
    request = request.override(tools=current_tools)
    print("current_tools: ", current_tools)

    return handler(request)


@tool
def read_data() -> str:
    """读取数据。"""
    print("running read_data")
    return f"Result of read data."


@tool
def write_data() -> str:
    """写入数据。"""
    print("running write_data")
    return f"Result of write data."


@tool
def delete_data() -> str:
    """删除数据"""
    print("running delete_data")
    return f"Result of delete data."


agent = create_agent(
    model=ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite"),
    tools=[read_data, write_data, delete_data],
    middleware=[context_based_tools],
    context_schema=Context
)
result = agent.invoke(
    {
        "messages": [{"role": "user", "content": "帮我读取、写入、删除数据"}]
    },
    context=Context(user_id="u01", user_role="editor")
)
print(result["messages"][-1].content)
