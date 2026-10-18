from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.runnables import RunnableConfig
from langsmith import uuid7

load_dotenv()


@tool
def get_weather(city: str) -> str:
    """Get weather for a given city"""
    return f"It's always sunny in {city}"


agent = create_agent(model="google_genai:gemini-3.1-flash-lite", tools=[get_weather])
config: RunnableConfig = {"configurable": {"thread_id": str(uuid7())}}
for chunk in agent.stream(
        {"messages": [{"role": "user", "content": "What is the weather in SF?"}]},
        stream_mode="messages",
        config=config,
        version="v2",
):
    if chunk["type"] == "messages":
        token, metadata = chunk["data"]
        print(f"Node: {metadata['langgraph_node']}")
        print(f"content: {token.content_blocks}")
        print("\n")
