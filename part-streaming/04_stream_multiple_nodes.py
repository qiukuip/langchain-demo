from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langgraph.config import get_stream_writer

load_dotenv()


@tool
def get_weather(city: str) -> str:
    """Get weather for a given city"""
    writer = get_stream_writer()
    writer(f"Looking up data for a city: {city}")
    writer(f"Accquired data for city: {city}")
    return f"It's always sunny in {city}"


agent = create_agent(model="google_genai:gemini-3.1-flash-lite", tools=[get_weather])

for chunk in agent.stream(
    {"messages": [{"role": "user", "content": "What is the weather in SF?"}]},
    stream_mode=["updates", "custom"],
    version="v2",
):
    print(f"stream_mode: {chunk['type']}")
    print(f"content: {chunk['data']}")
