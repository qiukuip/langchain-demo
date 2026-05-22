from typing import List

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langchain_core.messages import BaseMessage, HumanMessage

load_dotenv()


@tool("get_weather", description="获取某个地方的天气情况")
def get_weather(location: str) -> str:
    """获取某个地方的天气情况。"""
    return f"今日{location}的天气很好，适合出行。"


model = init_chat_model("google_genai:gemini-2.5-flash-lite")
model_with_tools = model.bind_tools([get_weather])
messages: List[BaseMessage] = [HumanMessage("今天巴黎的天气如何？")]
ai_messages = model_with_tools.invoke(messages)

messages.append(ai_messages)

for tool_call in ai_messages.tool_calls:
    print(f"Tool: {tool_call['name']}")
    print(f"Args: {tool_call['args']}")
    print(f"ID: {tool_call['id']}")

    if tool_call["name"] == "get_weather":
        tool_result = get_weather.invoke(tool_call)
        messages.append(tool_result)

final_response = model_with_tools.invoke(messages)
print(final_response)
