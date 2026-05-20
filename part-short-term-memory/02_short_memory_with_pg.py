import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import ToolRuntime, tool
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.postgres import PostgresSaver

load_dotenv()


@tool
def get_user_info(user_id: str, runtime: ToolRuntime) -> str:
    """Get user info for gaved user_id"""
    store = runtime.store
    user_info = store.get(("users",), user_id)
    if user_info is not None:
        return f"Username: {user_info.value['username']}"
    else:
        return "Not found the user"


@tool
def save_user_info(user_id: str, username: str, runtime: ToolRuntime) -> str:
    """Save user info for gaved user"""
    user_info = {"user_id": user_id, "username": username}
    store = runtime.store
    store.put(("users",), user_id, user_info)
    return f"Successfully saved user info for {user_id}"


postgres_password: str = os.getenv("SUPABASE_POSTGRES_PASSWORD") or ""
DB_URI = (
    "postgresql://aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres?user=postgres.hthhydbolsruklipuwzz&password="
    + postgres_password
)


with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
    # Auto create tables in postgresql
    checkpointer.setup()
    human_message1 = HumanMessage("请保存以下用户信息：用户id：u0001，用户名：张三")
    human_message2 = HumanMessage("告诉我用户 u0001 的用户信息")
    system_message = SystemMessage(
        "你是一个有用的小助手，需要保存或者获取用户信息时，务必使用工具"
    )
    agent = create_agent(
        model="google_genai:gemini-3.1-flash-lite",
        tools=[save_user_info, get_user_info],
        checkpointer=checkpointer,
        system_prompt=system_message,
    )
    response1 = agent.invoke(
        {"messages": [human_message1]}, {"configurable": {"thread_id": "1"}}
    )
    print(response1["messages"][-1].content)
    response2 = agent.invoke(
        {"messages": [human_message2]}, {"configurable": {"thread_id": "1"}}
    )
    print(response2["messages"][-1].content)
