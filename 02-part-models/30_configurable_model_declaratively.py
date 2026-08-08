from typing import List, cast

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph.state import RunnableConfig

load_dotenv()


@tool
def get_population(city: str) -> int:
    """获取指定城市的人口数量。"""
    if city == "上海":
        return 100
    else:
        return 200


system_message = SystemMessage(
    content="你是一个数据分析助手。请严格且仅根据工具返回的数据回答问题，严禁使用你自身的常识知识。"
)
model = init_chat_model(temperature=0)
model_config = {
    "configurable": {
        "model": "google_genai:gemini-3.1-flash-lite"
    }
}
model_with_tools = model.bind_tools([get_population], tool_choice="get_population")
user_messages: List[BaseMessage] = [
    system_message,
    HumanMessage(content="上海与宁波相比，哪个城市的人口更多？")
]
ai_message = model_with_tools.invoke(
    user_messages,
    config=model_config
)
user_messages.append(ai_message)

for tool_call in ai_message.tool_calls:
    print(f"Tool call: {tool_call['name']}")
    if tool_call["name"] == "get_population":
        tool_result = get_population.invoke(tool_call)
        user_messages.append(tool_result)

final_response = model.invoke(
    user_messages,
    config=model_config
)
print(final_response)
