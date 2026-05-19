from typing import List, Literal

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
from pydantic import BaseModel, Field

load_dotenv()


class WeatherInput(BaseModel):
    """Input for weather queries."""

    location: str = Field(description="City name or coordinates")
    units: Literal["celsius", "fahrenheit"] = Field(
        default="celsius", description="Temperature unit preference"
    )
    include_forecast: bool = Field(default=False, description="Include 5 days forecast")


# weather_schema = {
#     "type": "object",
#     "properties": {
#         "location": {"type": "string"},
#         "units": {"type": "string"},
#         "include_forecast": {"type": "boolean"},
#     },
#     "required": ["location", "units", "include_forecast"],
# }


# @tool(args_schema=weather_schema)
@tool(args_schema=WeatherInput)
def get_weather(
    location: str, units: str = "celsius", include_forecast: bool = False
) -> str:
    """Get current weather and optional forecase"""
    temp = 22 if units == "celsius" else 72
    result = f"Current weather in {location}: {temp} degrees {units[0].upper()}"
    if include_forecast:
        result += "\nNext 5 days: Sunny"
    return result


model = init_chat_model("google_genai:gemini-3.1-flash-lite")
model_with_tools = model.bind_tools([get_weather])
system_message = SystemMessage(
    "You are a helpful assistant, when need to get weather info, must call the weather tool"
)
human_message = HumanMessage(
    "Tell me the weather in Paris today and the weather forecast"
)
messages: List[BaseMessage] = [system_message, human_message]
ai_message = model_with_tools.invoke(messages)
messages.append(ai_message)

for tool_call in ai_message.tool_calls:
    print(f"Tool: {tool_call['name']}")
    print(f"Args: {tool_call['args']}")
    print(f"ID: {tool_call['id']}")
    if tool_call["name"] == "get_weather":
        tool_result = get_weather.invoke(tool_call)
        messages.append(tool_result)

final_response = model_with_tools.invoke(messages)
print(final_response)
