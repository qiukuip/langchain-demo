from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langgraph.prebuilt import ToolRuntime

load_dotenv()


@tool
def get_weather(city: str, runtime: ToolRuntime) -> str:
    """Get weather info for a city."""
    # Execution info
    execution_info = runtime.execution_info
    print(f"Thread => {execution_info.thread_id}, Run => {execution_info.run_id}")
    server_info = runtime.server_info
    if server_info is not None:
        print(f"Assistant => {server_info.assistant_id}")
        if server_info.user is not None:
            print(f"User => {server_info.user}")

    if city.startswith(("A", "B")):
        return f"Is's sunny in {city}."
    else:
        return f"Is's rainy at {city}."


agent = create_agent(
    model="ollama:llama3.1",
    tools=[get_weather]
)
messages = [HumanMessage(content="What's the weather in SF?")]
config: RunnableConfig = {"configurable": {"thread_id": "1202"}}
response = agent.invoke(
    {"messages": messages},
    config=config
)
print(response["messages"][-1].content_blocks)
