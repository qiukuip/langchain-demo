from dataclasses import dataclass

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain.tools import ToolRuntime, tool
from langchain_core.runnables import RunnableConfig
from langgraph.store.memory import InMemoryStore


@dataclass
class CustomContext:
    user_id: str


store = InMemoryStore()


@tool
def get_user_info(runtime: ToolRuntime[CustomContext]) -> str:
    """Get user information for a given user_id"""
    assert runtime.store is not None
    user_id = runtime.context.user_id
    user_info = runtime.store.get(("users",), user_id)
    return str(user_info.value) if user_info else "Unknown user"


@tool
def save_user_info(username: str, runtime: ToolRuntime[CustomContext]) -> str:
    """Save the current user's username in long-term memory."""
    assert runtime.store is not None
    user_id = runtime.context.user_id
    runtime.store.put(("users",), user_id, {"user_id": user_id, "username": username})
    return "Successfully saved user information"


load_dotenv()
config: RunnableConfig = {
    "configurable": {
        "thread_id": "1802"
    }
}
agent = create_agent(
    model="ollama:llama3.1",
    tools=[save_user_info, get_user_info],
    store=store,
    context_schema=CustomContext,
    system_prompt=(
        "Use the memory tools for all user information. When asked to save a "
        "username, call save_user_info. When asked to look up information, "
        "call get_user_info before answering. Never guess stored values."
    ),
)
result1 = agent.invoke(
    {"messages": [HumanMessage("Save my username as Alice.")]},
    context=CustomContext(user_id="user_123"),
    config=config,
    version="v2"
)
for msg in result1["messages"]:
    msg.pretty_print()
print("=====")
result2 = agent.invoke(
    {"messages": [HumanMessage("Look up my saved information using memory and tell me what it says.")]},
    context=CustomContext(user_id="user_123"),
    config=config,
    version="v2",
)
for msg in result2["messages"]:
    msg.pretty_print()
