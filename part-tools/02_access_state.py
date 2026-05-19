from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import ToolRuntime, tool
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from user_preference import UserPreference

load_dotenv()


@tool
def get_last_user_message(runtime: ToolRuntime) -> str:
    """Get the most recent message from user"""

    messages = runtime.state["messages"]
    for message in reversed(messages):
        if isinstance(message, HumanMessage):
            return str(message.content)
    return "No user messages found"


@tool
def get_user_preference(preference_name: str, runtime: ToolRuntime) -> str:
    """Get a user preference value. preference_name: language"""
    preferences = runtime.state["user_preferences"] | {}
    return preferences.get(preference_name, "Not set")


system_message = SystemMessage(
    "你是一个有用的助手，尽你所能回答问题。当要获取用户偏好设置时，务必使用工具。如果你知道该如何回答，请直接回答暂无法解答该问题，请勿编造。"
)
human_message1 = HumanMessage("什么是恒星年？")
human_message2 = HumanMessage("什么是回归年？")
# human_message3 = HumanMessage("用户最后一条消息是什么？")
human_message3 = HumanMessage("用户首选语言是什么？")
ai_message1 = AIMessage("行星公转周期即为恒星年。")
ai_message2 = AIMessage("恒星回到黄道上相同的点所经历的时间即为回归年。")
messages = [human_message1, ai_message1, human_message2, ai_message2, human_message3]

model = init_chat_model("google_genai:gemini-3.1-flash-lite")
agent = create_agent(
    model=model,
    tools=[get_last_user_message, get_user_preference],
    state_schema=UserPreference,
)
response = agent.invoke({"messages": messages, "user_preferences": {"language": "Chinese"}})
print(response["messages"][-1].content)
