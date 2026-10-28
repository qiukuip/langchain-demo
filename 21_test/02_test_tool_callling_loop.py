from langchain.agents import create_agent
from langchain.messages import AIMessage, HumanMessage, ToolCall
from langchain.tools import tool
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel


class FakeToolCallingModel(GenericFakeChatModel):
    def bind_tools(self, tools, **kwargs):
        return self


@tool
def get_weather(city: str) -> str:
    """Get the weather for a city."""
    return f"72°F and sunny in {city}"


def test_agent_calls_tool_then_answers():
    model = FakeToolCallingModel(messages=iter([
        # Turn 1: the model calls the tool
        AIMessage(
            content="",
            tool_calls=[ToolCall(name="get_weather", args={"city": "Tokyo"}, id="call_1")],
        ),
        # Turn 2: the model answers using the tool result
        AIMessage(content="It is 72°F and sunny in Tokyo."),
    ]))
    agent = create_agent(model, tools=[get_weather])
    result = agent.invoke({"messages": [HumanMessage(content="Weather in Tokyo?")]})

    tool_call_messages = [
        m for m in result["messages"] if isinstance(m, AIMessage) and m.tool_calls
    ]
    assert len(tool_call_messages) == 1
    assert tool_call_messages[0].tool_calls[0]["name"] == "get_weather"
    assert "Tokyo" in result["messages"][-1].text
