from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import ToolRuntime, tool

load_dotenv()


@tool
def get_weather(city: str, runtime: ToolRuntime) -> str:
    """Get weather for a given city"""
    writer = runtime.stream_writer
    # writer 必须在 LangGraph 中且 stream_mode 包含 custom 才能生效，create_agent 本质上也是一个 Graph
    writer(f"Looking up data for city: {city}")
    writer(f"Acquired data for city: {city}")

    info = runtime.execution_info
    print(f"Thread: {info.thread_id}, Run: {info.run_id}")
    print(f"Attempt: {info.node_attempt}")

    # server info is None when tools are not running on LangGraph Server
    server_info = runtime.server_info
    if server_info is not None:
        print(f"Assistant: {server_info.assistant_id}, Graph: {server_info.graph_id}")
        if server_info.user is not None:
            print(f"user: {server_info.user.identity}")

    return f"It's always sunny in {city}"


model = init_chat_model("google_genai:gemini-3.1-flash-lite")
agent = create_agent(model=model, tools=[get_weather])

for event in agent.stream(
        {"messages": [{"role": "user", "content": "What's the weather in New York?"}]},
        config={
            "configurable": {
                "thread_id": "thread_0406"
            }
        },
        stream_mode=["custom", "messages"],
):
    print(event)
