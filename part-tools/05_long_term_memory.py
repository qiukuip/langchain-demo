from typing import Any
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import ToolRuntime, tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.store.memory import InMemoryStore

load_dotenv()


@tool
def get_user_info(user_id: str, runtime: ToolRuntime) -> str:
    """Look up user info."""
    store = runtime.store 
    user_info = store.get(("users",), user_id)
    return str(user_info.value) if user_info else "Unknown user"


@tool
def save_user_info(user_id: str, user_info: dict[str, Any], runtime: ToolRuntime) -> str:
    """Save user info"""
    store = runtime.store
    store.put(("users",), user_id, user_info)
    return "Successfully saved user info"


model = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")
store = InMemoryStore()
agent = create_agent(model=model, tools=[save_user_info, get_user_info], store=store)
response1 = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "Save the following user: user_id: abc123, name: Foo, age: 25, email: foo@langchain.dev",
            }
        ]
    }
)
print(response1["messages"][-1].content_blocks)
print("=====")
response2 = agent.invoke(
    {"messages": [{"role": "user", "content": "Get user info for user with id abc123"}]}
)
print(response2["messages"][-1].content_blocks)
