import pytest
from langchain.agents import create_agent
from langchain.messages import AIMessage, HumanMessage, ToolCall
from langchain_core.language_models import GenericFakeChatModel
from langchain_core.tools import tool


class FakeToolCallingModel(GenericFakeChatModel):
    def bind_tools(self, tools, **kwargs):
        return self


@tool
def get_weather(city: str) -> str:
    """Get the weather for a city."""
    return f"72°F and sunny in {city}"


@pytest.fixture
def weather_model():
    return FakeToolCallingModel(messages=iter([
        AIMessage(
            content="",
            tool_calls=[ToolCall(name="get_weather", args={"city": "Tokyo"}, id="call_1")],
        ),
        AIMessage(content="It is 72°F and sunny in Tokyo."),
    ]))


def test_tool_is_called(weather_model):
    agent = create_agent(weather_model, tools=[get_weather])
    result = agent.invoke({"messages": [HumanMessage(content="Weather in Tokyo?")]})
    tool_call_messages = [
        m for m in result["messages"] if isinstance(m, AIMessage) and m.tool_calls
    ]
    assert tool_call_messages[0].tool_calls[0]["name"] == "get_weather"


def test_final_response(weather_model):
    agent = create_agent(weather_model, tools=[get_weather])
    result = agent.invoke({"messages": [HumanMessage(content="Weather in Tokyo?")]})
    assert "Tokyo" in result["messages"][-1].text
