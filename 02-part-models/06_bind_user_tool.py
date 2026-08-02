from typing import List

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langchain_core.messages import BaseMessage, HumanMessage

load_dotenv()


@tool
def get_weather(location: str) -> str:
    """获取某个地点的天气。"""
    return f"{location}的天气：晴。"


model = init_chat_model(model="google_genai:gemini-3.1-flash-lite")
messages: List[BaseMessage] = [
    HumanMessage("波士顿和东京的天气怎么样？")
]
# 一般模型默认开启并行 parallel_tool_calls=True
# model_with_tools = model.bind_tools([get_weather], parallel_tool_calls=True)
# 强制使用工具
model_with_tools = model.bind_tools([get_weather], tool_choice="get_weather")
ai_msg = model_with_tools.invoke(messages)
print(ai_msg.tool_calls)
messages.append(ai_msg)

for tool_call in ai_msg.tool_calls:
    if tool_call["name"] == "get_weather":
        print(f"tool_call_id: {tool_call['id']}")
        tool_result = get_weather.invoke(tool_call)
        messages.append(tool_result)

final_response = model_with_tools.invoke(messages)
print(final_response.text)
