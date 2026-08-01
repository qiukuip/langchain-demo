from dotenv import load_dotenv
from langchain.agents import create_agent

load_dotenv(verbose=True)


def get_weather(city: str) -> str:
    """Get weather from city"""
    return f"It's sunny at {city}"


agent = create_agent(
    model="google_genai:gemini-2.5-flash-lite",
    tools=[get_weather],
    system_prompt="You are a helpful assistant"
)
result = agent.invoke(
    {"messages": [{"role": "user", "content": "What's the weather in SF?"}]}
)
print(result["messages"][-1].content_blocks)
