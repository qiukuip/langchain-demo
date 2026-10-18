from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt._tool_call_transformer import ToolCallTransformer

load_dotenv()


@tool
def get_weather(city: str) -> str:
    """Get weather for a given city"""
    return f"It's always sunny in {city}"


config: RunnableConfig = {"configurable": {"thread_id": "0701"}}
agent = create_agent(model="google_genai:gemini-3.1-flash-lite", tools=[get_weather])
stream = agent.stream_events(
    {"messages": [{"role": "user", "content": "What is the weather in SF?"}]},
    config=config,
    version="v3",
    transformers=[ToolCallTransformer]
)
for kind, item in stream.interleave("messages", "tool_calls"):
    if kind == "messages":
        for token in item.text:
            print(token, end="", flush=True)
    elif kind == "tool_calls":
        print(f"Tool call - {item.tool_name}: {item.input}")
        for delta in item.output_deltas:
            print(delta, end="", flush=True)
        print(f"Tool result: {item.output}")

final_state = stream.output
