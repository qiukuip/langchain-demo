from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool


@tool
def get_weather(city: str) -> str:
    """Get weather for a city"""
    return f"It's windy at {city}"


load_dotenv()
model = init_chat_model(
    model="gemini-3.1-flash-lite",
    model_provider="google_genai"
)
model_with_tools = model.bind_tools([get_weather], tool_choice="any")
messages = [HumanMessage(content="What's the weather in Boston and Tokyo?")]
ai_message = model_with_tools.invoke(messages)
messages.append(ai_message)

for tool_call in ai_message.tool_calls:
    tool_call_name = tool_call["name"]
    print(f"tool_call_name: {tool_call_name}")
    if tool_call_name == "get_weather":
        tool_result = get_weather.invoke(tool_call)
        print(f"tool_result: {tool_result}")
        messages.append(tool_result)

final_response = model.invoke(messages)
print(final_response.content)
