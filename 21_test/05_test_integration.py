import pytest
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain_core.tools import tool


@tool
def get_weather(city: str) -> str:
    """Get the weather for a city."""
    return f"72°F and sunny in {city}"


@pytest.mark.integration
def test_agent_with_real_model():
    agent = create_agent("ollama:llama3.1", tools=[get_weather])
    result = agent.invoke({
        "messages": [HumanMessage(content="What's the weather in SF?")]
    })
    assert len(result["messages"]) > 1
