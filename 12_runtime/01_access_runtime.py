from dataclasses import dataclass
from typing import Any, List

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import ToolRuntime
from langgraph.store.memory import InMemoryStore

load_dotenv()


@dataclass
class CustomContext:
    user_id: str
    username: str
    email: str


@tool()
def save_user_info(runtime: ToolRuntime[CustomContext]) -> str:
    """Save the user information."""
    user_id = runtime.context.user_id
    username = runtime.context.username
    email = runtime.context.email
    store = runtime.store
    if store.get(("user_info",), user_id) is not None:
        return f"user {user_id}'s info had been saved."
    else:
        store.put(("user_info",), user_id, {"username": username, "email": email})
        return f"user {user_id}'s info has been saved."


@tool()
def load_user_info(runtime: ToolRuntime[CustomContext]) -> str | None:
    """Load the user information."""
    store = runtime.store
    user_id = runtime.context.user_id
    if user_id is None:
        return None
    user_info_mapping = store.get(("user_info",), user_id)
    if user_info_mapping is None:
        return None
    user_info: dict = user_info_mapping.value
    return f"user {user_id}'s username is {user_info['username']}, email is {user_info['email']}."


agent = create_agent(
    model="ollama:llama3.1",
    tools=[save_user_info, load_user_info],
    middleware=[
        PIIMiddleware[Any, CustomContext](
            pii_type="email", strategy="mask", apply_to_tool_results=True
        )
    ],
    context_schema=CustomContext,
    checkpointer=InMemorySaver(),
    store=InMemoryStore(),
)
messages1: List[BaseMessage] = [
    HumanMessage(content="记住我的信息。")
]
config: RunnableConfig = {"configurable": {"thread_id": "thread_1201"}}
response1 = agent.invoke(
    {"messages": messages1},
    context=CustomContext(user_id="123", username="aid", email="aid@happ.com"),
    config=config
)
print(response1["messages"][-1].content_blocks)
print("=====")

messages2: List[BaseMessage] = [HumanMessage("查询用户 id 为 123 的用户信息")]
response2 = agent.invoke(
    {"messages": messages2},
    context=CustomContext(user_id="123", username="aid", email="aid@happ.com"),
    config=config
)
print(response2["messages"][-1].content_blocks)
