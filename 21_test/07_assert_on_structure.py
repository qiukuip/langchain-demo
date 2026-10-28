from langchain.agents import create_agent
from langchain.messages import AIMessage, HumanMessage
from langchain_core.tools import tool


@tool
def get_weather(city: str) -> str:
    """Get the weather for a city."""
    return f"72°F and sunny in {city}"


def test_agent_calls_weather_tool():
    agent = create_agent(
        model="ollama:llama3.1",
        tools=[get_weather]
    )
    result = agent.invoke({
        "messages": [HumanMessage(content="What's the weather in SF?")]
    })

    messages = result["messages"]
    tool_calls = [
        tc
        for msg in messages
        if hasattr(msg, "tool_calls")
        for tc in (msg.tool_calls or [])
    ]

    assert any(tc["name"] == "get_weather" for tc in tool_calls)
    assert isinstance(messages[-1], AIMessage)
    assert len(messages[-1].content) > 0
