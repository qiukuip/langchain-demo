from dataclasses import dataclass

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import ToolRuntime
from langsmith import uuid7


@dataclass
class Context:
    user_id: str
    user_name: str


@dynamic_prompt
def user_context_prompt(request: ModelRequest) -> str:
    """将用户信息注入提示词中"""
    context = request.runtime.context
    user_id = context.user_id
    user_name = context.user_name
    return f"当前用户信息: 用户id是 {user_id}，用户姓名是: {user_name}"


@tool
def get_current_user_info(runtime: ToolRuntime[Context]) -> str:
    """获取当前用户的信息"""
    context = runtime.context
    user_id = context.user_id
    user_name = context.user_name
    info = f"当前用户id是: {user_id}, 当前用户姓名是: {user_name}"
    print(info)
    return info


load_dotenv()
checkpointer = InMemorySaver()
agent = create_agent(
    model=ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite", temperature=0.5, max_tokens=10000),
    tools=[get_current_user_info],
    context_schema=Context,
    checkpointer=checkpointer,
    # middleware=[user_context_prompt]
)
result = agent.invoke(
    {"messages": [HumanMessage("我的名字是什么？")]},
    config={"configurable": {"thread_id": str(uuid7())}},
    context=Context(user_id="u01", user_name="Tom")
)
for message in result["messages"]:
    print(message.content_blocks)
