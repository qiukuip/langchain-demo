from dataclasses import dataclass
from typing import TypedDict

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.structured_output import ProviderStrategy
from langchain.messages import HumanMessage
from langchain.tools import ToolRuntime, tool
from langgraph.store.memory import InMemoryStore


@dataclass
class CustomContext:
    user_id: str


class UserInfo(TypedDict):
    username: str


store = InMemoryStore()


@tool
def get_user_info(runtime: ToolRuntime[CustomContext]) -> str:
    """Get user information for a given user_id"""
    assert runtime.store is not None
    user_id = runtime.context.user_id
    user_info = runtime.store.get(("users",), user_id)
    return str(user_info.value) if user_info else "Unknown user"


@tool
def save_user_info(user_info: UserInfo, runtime: ToolRuntime[CustomContext]) -> str:
    """Save user information"""
    assert runtime.store is not None
    user_id = runtime.context.user_id
    store.put(("users",), user_id, dict(user_info))
    return "Successfully saved user information"


load_dotenv()
agent = create_agent(
    model="google_genai:gemini-3.1-flash-lite",
    tools=[save_user_info, get_user_info],
    store=store,
    context_schema=CustomContext,
    response_format=ProviderStrategy(UserInfo),
)
result1 = agent.invoke(
    {"messages": [HumanMessage("Save my information: username: Alice")]},
    context=CustomContext(user_id="user_123"),
)
for msg in result1["messages"]:
    msg.pretty_print()
print("=====")
result2 = agent.invoke(
    {
        "messages": [HumanMessage("look up user information")],
    },
    context=CustomContext(user_id="user_123"),
)
for msg in result2["messages"]:
    msg.pretty_print()
