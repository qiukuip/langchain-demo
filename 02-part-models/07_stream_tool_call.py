from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool

load_dotenv()


@tool
def get_weather(city: str) -> str:
    """Get weather for given city"""
    return f"It's cloudy at {city}"


model = init_chat_model(model="google_genai:gemini-3.1-flash-lite")
model_with_tools = model.bind_tools([get_weather], tool_choice="get_weather")
for chunk in model_with_tools.stream("波士顿的天气怎么样？"):
    for tool_chunk in chunk.tool_call_chunks:
        if name := tool_chunk.get("name"):
            print(f"Tool: {name}")
        if id_ := tool_chunk.get("id"):
            print(f"ID: {id_}")
        if args := tool_chunk.get("args"):
            print(f"Args: {args}")
