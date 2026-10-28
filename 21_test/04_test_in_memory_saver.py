from langchain.agents import create_agent
from langchain_core.language_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver


class FakeModel(GenericFakeChatModel):
    def bind_tools(self, tools, **kwargs):
        return self


def test_in_memory_saver():
    model = FakeModel(messages=iter([
        AIMessage(content="It's rainy in Tokyo."),
        AIMessage(content="I remember the earlier question about Tokyo."),
    ]))
    agent = create_agent(
        model=model,
        checkpointer=InMemorySaver(),
    )
    config: RunnableConfig = {
        "configurable": {
            "thread_id": "session-1",
        }
    }
    # First invocation
    response = agent.invoke(
        {"messages": [HumanMessage(content="What's the weather in Tokyo?")]},
        config=config
    )
    assert response["messages"][-1].content == "It's rainy in Tokyo."

    # The same thread restores the first invocation's messages before adding this turn.
    response = agent.invoke(
        {"messages": [HumanMessage(content="What did I ask about earlier?")]},
        config=config,
    )
    messages = response["messages"]
    human_messages = [message.content for message in messages if isinstance(message, HumanMessage)]

    assert human_messages == [
        "What's the weather in Tokyo?",
        "What did I ask about earlier?",
    ]
    assert "Tokyo" in messages[-1].content
