from dotenv import load_dotenv
from google.genai.types import ThinkingConfig
from langchain.agents import create_agent
from langchain.messages import AIMessageChunk
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.config import get_stream_writer
from langgraph.graph.state import Runnable

load_dotenv()


@tool
def get_weather(city: str) -> str:
    """Get weather for a given city"""
    writer = get_stream_writer()
    writer(f"Looking up data for a city: {city}")
    writer(f"Accquired data for city: {city}")
    return f"It's always sunny in {city}"


model = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    config=ThinkingConfig(include_thoughts=True, thinking_budget=1024)
)
agent: Runnable = create_agent(
    model=model,
    tools=[get_weather]
)

for chunk in agent.stream(
    {"messages": [{"role": "user", "content": "What is the weather in SF?"}]},
    stream_mode="messages",
    version="v2"
):
    print(f"chunk type: {chunk['type']}")
    if not isinstance(chunk, AIMessageChunk):
       continue
    reasoning = [b for b in chunk.content_blocks if b["type"] == "reasoning"]
    text = [b for b in chunk.content_blocks if b["type"] == "text"]
    if reasoning:
       print(f"[thinking] {reasoning[0]['text']}", end="")
    if text:
       print(text[0]["text"], end="")
