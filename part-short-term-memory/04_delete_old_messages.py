from typing import Any

from dotenv import load_dotenv
from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import after_model
from langchain_core.messages import RemoveMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.state import RunnableConfig
from langgraph.runtime import Runtime

load_dotenv()


@after_model
def delete_messages(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    """Delete old messages to keep conversation manageable"""
    messages = state["messages"]
    if len(messages) > 2:
        return {"messages": [RemoveMessage(id=str(m.id)) for m in messages[:2]]}
    return None


agent = create_agent(
    model="google_genai:gemini-3.1-flash-lite",
    tools=[],
    middleware=[delete_messages],
    checkpointer=InMemorySaver(),
)
config: RunnableConfig = {"configurable": {"thread_id": "1"}}
for event in agent.stream(
    {"messages": [{"role": "user", "content": "你好，我是爱丽丝。"}]},
    config=config,
    stream_mode="values",
):
    print([(message.type, message.content) for message in event["messages"]])

for event in agent.stream(
    {"messages": [{"role": "user", "content": "我的名字是什么？"}]},
    config=config,
    stream_mode="values",
):
    print([(message.type, message.content) for message in event["messages"]])
