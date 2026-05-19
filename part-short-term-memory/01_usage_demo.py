from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import ToolRuntime, tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore

load_dotenv()


@tool
def get_user_info(user_id: str, runtime: ToolRuntime) -> str:
    """Get user info for the given user id"""
    store = runtime.store
    user_info = store.get(("users",), user_id)
    if user_info is not None:
        return f"Username: {str(user_info.value)}"
    else:
        return "Not found the user"


@tool
def save_user_info(user_id: str, username: str, runtime: ToolRuntime) -> str:
    """Save user info for user"""
    user_info = {"user_id": user_id, "username": username}
    store = runtime.store
    store.put(("users",), user_id, user_info)
    return "Successfully saved user info"


agent = create_agent(
    model="google_genai:gemini-3.1-flash-lite",
    tools=[save_user_info, get_user_info],
    checkpointer=InMemorySaver(),
    store=InMemoryStore()
)
response1 = agent.invoke(
    {"messages": [{"role": "user", "content": "Hi! My name is Alice."}]},
    {"configurable": {"thread_id": "1"}},
)
print(response1["messages"][-1].content_blocks)
print("=====")
response2 = agent.invoke(
    {"messages": [{"role": "user", "content": "What's my name?"}]},
    {"configurable": {"thread_id": "2"}},
)
print(response2["messages"][-1].content_blocks)
