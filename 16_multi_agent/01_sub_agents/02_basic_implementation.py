from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool

load_dotenv()


@tool("weather_tool", description="Get weather information")
def get_weather(city: str) -> str:
    """Get weather information for a given city"""
    return f"It's rainny today in {city}"


weather_agent = create_agent(
    model="google_genai:gemini-3.1-flash-lite", tools=[get_weather]
)


@tool("weather_agent_tool", description="Get weather information by subagent")
def call_weather_agent(city: str) -> str:
    """Get weather information by subagent"""
    result = weather_agent.invoke(
        {"messages": [{"role": "user", "content": f"Tell me the weather in {city}"}]}
    )
    return result["messages"][-1].content


agent = create_agent(
    model="google_genai:gemini-3.1-flash-lite", tools=[call_weather_agent]
)
result = agent.invoke(
    {"messages": [{"role": "user", "content": "What's the weather in SF?"}]}
)
print(result["messages"][-1].content)
