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
    stream = await supervisor.astream_events(
        {"messages": [{"role": "user", "content": "What is the weather in Boston?"}]},
        version="v3",
    )

    async for subagent in stream.subgraphs:
        if subagent.graph_name != "weather_agent":
            continue

        print(f"[{subagent.graph_name}]: ", end="")

        async for message in subagent.messages:
            print(await message.text)
            async for token in message.text:
                print(token, end="", flush=True)

            full_msg = message.output
            if full_msg:
                print(full_msg)

            async for call in message.tool_calls:
                print(await call.tool_name)
                print(await call.input)
        print()

    print(stream.output)


asyncio.run(main())
