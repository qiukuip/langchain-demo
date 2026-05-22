from typing import Any

from dotenv import load_dotenv
from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import before_model
from langchain_core.messages import HumanMessage, RemoveMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langgraph.graph.state import RunnableConfig
from langgraph.runtime import Runtime

load_dotenv()


@before_model
def trim_messages(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    """Keep only the last few messages to fit context window"""
    messages = state["messages"]
    message_count = len(messages)
    if message_count < 3:
        return None
    most_recent_message = messages[0]
    recent_messages = messages[-3:] if message_count % 2 == 0 else messages[-4:]
    new_messages = [most_recent_message] + recent_messages
    return {"messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES), *new_messages]}


agent = create_agent(
    model="google_genai:gemini-3.1-flash-lite",
    tools=[],
    middleware=[trim_messages],
    checkpointer=InMemorySaver(),
)
config: RunnableConfig = {"configurable": {"thread_id": "1"}}
agent.invoke({"messages": [HumanMessage("你好！我的名字叫鲍勃！")]}, config=config)
agent.invoke({"messages": [HumanMessage("写一首关于猫的短诗。")]}, config=config)
agent.invoke({"messages": [HumanMessage("再写一个关于狗的。")]}, config=config)
response = agent.invoke({"messages": [HumanMessage("我的名字是什么？")]}, config=config)
print(response["messages"][-1].pretty_print())
