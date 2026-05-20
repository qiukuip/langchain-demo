from dotenv import load_dotenv
from langchain.agents import create_agent


load_dotenv()


def get_weather(city: str) -> str:
    """Get weather for a city."""
    return f"It's always sunny in {city}!"


agent = create_agent(
    model="google_genai:gemini-3.1-flash-lite",
    tools=[get_weather],
)

stream = agent.stream_events(
    {
        "messages": [{"role": "user", "content": "What is the weather in SF?"}],
    },
    version="v3",
)

for message in stream.messages:
    print(f"[{message.node}] ", end="")
    for delta in message.text:
        print(delta, end="", flush=True)

    for delta in message.reasoning:
        print(f"[thinking] {delta}", end="", flush=True)

    for chunk in message.tool_calls:
        print(f"tool call chunk: {chunk}")
    finalized = message.tool_calls.get()
    if finalized:
        print(f"finalized tool calls: {finalized}")

    full_message = message.output
    usage = full_message.usage_metadata
    if usage:
        print(usage)

