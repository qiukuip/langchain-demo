from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool


@tool
def get_weather(city: str) -> str:
    """Get weather for a city"""
    return f"It's cloudy at {city}"


load_dotenv()
model = init_chat_model(
    model="gemini-3.1-flash-lite",
    model_provider="google_genai"
)
model_with_tools = model.bind_tools([get_weather], tool_choice="any")
messages = [HumanMessage(content="What's the weather in Boston and Tokyo?")]
for chunk in model_with_tools.stream(messages):
    for tool_chunk in chunk.tool_call_chunks:
        if name := tool_chunk.get("name"):
            print(f"Tool: {name}")
        if _id := tool_chunk.get("id"):
            print(f"ID: {_id}")
        if args := tool_chunk.get("args"):
            print(f"Args: {args}")
