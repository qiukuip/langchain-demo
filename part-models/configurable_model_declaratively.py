import os
from typing import List, cast

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph.state import RunnableConfig

load_dotenv()


@tool
def get_population(city: str) -> int:
    """获取指定城市的人口数量。"""
    if city == "上海":
        return 100
    else:
        return 200


model = init_chat_model(api_key=os.getenv("GOOGLE_API_KEY"), temperature=0)
model_config = {
    "configurable": {
        "model": "google_genai:gemini-3.1-flash-lite"
    }
}
model_with_tools = model.bind_tools([get_population])
# user_messages = [{"role": "user", "content": "上海与宁波相比，哪个城市的人口更多？"}]
user_messages: List[BaseMessage] = [HumanMessage(content="上海与宁波相比，哪个城市的人口更多？")]
ai_message = model_with_tools.invoke(
    user_messages,
    config=cast(RunnableConfig, model_config)
)
user_messages.append(ai_message)

for tool_call in ai_message.tool_calls:
    if tool_call["name"] == "get_population":
        tool_result = get_population.invoke(tool_call)
        user_messages.append(tool_result)

final_response = model_with_tools.invoke(
    user_messages,
    config=cast(RunnableConfig, model_config)
)
print(final_response)
