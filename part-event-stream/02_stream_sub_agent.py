import asyncio
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool

load_dotenv()


@tool
def get_weather(city: str) -> str:
    """Get the weather in a city"""
    return f"It's always sunny in {city}"


weather_agent = create_agent(
    model="google_genai:gemini-3.1-flash-lite",
    tools=[get_weather],
    name="weather_agent",
)


@tool
def call_weather(query: str) -> str:
    """Query the weather agent"""
    result = weather_agent.invoke({"messages": [{"role": "user", "content": query}]})
    return result["messages"][-1].text


supervisor = create_agent(
    model="google_genai:gemini-3.1-flash-lite", tools=[call_weather], name="supervisor"
)


async def main():
    stream = supervisor.stream_events(
        {"messages": [{"role": "user", "content": "What is the weather in Boston?"}]},
        version="v3",
    )
    for subagent in stream.subgraphs:
        if subagent["graph_name"] != "weather_agent":
            continue
        print(f"{subagent.graph_name}", end="")
        for message in subagent.messages:
            for token in message.text:
                print(token, end="", flush=True)
            print(message.output)
        print()
    print(stream.output)


asyncio.run(main())
