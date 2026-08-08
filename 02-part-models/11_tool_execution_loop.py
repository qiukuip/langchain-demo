from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool


@tool
def get_weather(city: str) -> str:
    """Gets weather for a city"""
    return f"It's rainy at {city}"


load_dotenv()
model = init_chat_model(
    model="gemini-2.5-flash-lite",
    model_provider="google_genai",
    temperature=0.2,
    max_tokens=100,
    timeout=600
)
model_with_tools = model.bind_tools([get_weather])
messages = [{"role": "user", "content": "What's the weather in Boston?"}]
ai_message = model_with_tools.invoke(messages)
messages.append(ai_message)

for tool_call in ai_message.tool_calls:
    tool_result = get_weather.invoke(tool_call)
    messages.append(tool_result)

final_response = model_with_tools.invoke(messages)
print(final_response.text)
