from custom_state import CustomState
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import ToolRuntime, tool
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage, human
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.types import Command

load_dotenv()


@tool
def set_username(new_username: str, runtime: ToolRuntime[None, CustomState]) -> Command:
    """Set the user's name in the conversation state"""
    return Command(
        update={
            "username": new_username,
            "messages": [
                ToolMessage(
                    content=f"Username set to {new_username}",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )


@tool
def get_username(runtime: ToolRuntime) -> str:
    """Get the user's name from the conversation state"""
    custom_state = runtime.state | {}
    return custom_state.get("username", "Unknown")


system_message = SystemMessage(
    "你是一个有用的助手，当需要修改用户信息时请务必使用工具。"
)
human_message1 = HumanMessage("请修改用户的名字为 Bob。")
human_message2 = HumanMessage("用户的名字是什么？")
messages = [system_message, human_message1, human_message2]
agent = create_agent(
    model=ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite"),
    tools=[set_username, get_username],
    state_schema=CustomState,
)
response = agent.invoke({"messages": messages, "custom_state": {"username": "张三"}})
print(response["messages"][-1].content)
