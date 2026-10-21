from typing import TypedDict, Any

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.prebuilt import ToolRuntime

load_dotenv()


class UserInfoState(TypedDict):
    user_id: str


@tool
def get_user_info(runtime: ToolRuntime) -> dict[str, Any] | str:
    """Query user information."""
    user_id = runtime.state["user_id"]
    return {
        "user_id": user_id,
        "email": "aid@happ.com",
        "key": "sk-123456789123456789"
    } \
        if user_id == "u1" \
        else "User info not found!"


agent = create_agent(
    model="ollama:llama3.1",
    tools=[get_user_info],
    state_schema=UserInfoState,
    middleware=[
        PIIMiddleware(
            pii_type="email",
            strategy="mask",
            apply_to_input=True,
            apply_to_tool_results=True
        ),
        PIIMiddleware(
            pii_type="custom",
            strategy="hash",  # mask/block/redact/hash
            detector=r"sk-[0-9A-Za-z]{18}",
            apply_to_tool_results=True,
        )
    ]
)
response = agent.invoke(
    {
        "messages": [HumanMessage(content="请查找我的信息。")],
        "user_id": "u1"
    }
)
for msg in response["messages"]:
    print(msg.pretty_print())
