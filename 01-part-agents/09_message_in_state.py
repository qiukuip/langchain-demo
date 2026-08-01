import uuid

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver
from langsmith import uuid7


@tool
def get_weather(city: str) -> str:
    """Get weather for city"""
    return f"It's rainy at {city} today, it's sunny at {city} tomorrow."


load_dotenv()

checkpointer = InMemorySaver()
model = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    max_tokens=20000,
    timeout=600
)
agent = create_agent(
    model=model,
    tools=[get_weather],
    checkpointer=checkpointer
)
thread_id = str(uuid7())
result = agent.invoke(
    {"messages": [{"role": "user", "content": "What's the weather in SF?"}]},
    config={"configurable": {"thread_id": thread_id}}
)
print(result["messages"][-1].content_blocks)
print("\n")
agent.invoke(
    {"messages": [HumanMessage("What about tomorrow?")]},
    config={"configurable": {"thread_id": thread_id}}
)
print(result["messages"][-1].content_blocks)
