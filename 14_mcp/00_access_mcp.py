import asyncio

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()


async def main():
    client = MultiServerMCPClient(
        {
            "math": {
                "transport": "stdio",
                "command": "python",
                "args": ["servers/math_server.py"],
            },
            "weather": {
                "transport": "streamable_http",
                "url": "http://localhost:8001/mcp",
                "headers": {
                    "Authorization": "Bearer custom_token",
                    "X-Auth-Token": "Custom-Header-Value",
                },
            },
        }
    )

    tools = await client.get_tools()
    for tool in tools:
        print(f"{tool.name}: {tool.description}")
    agent = create_agent(model="ollama:llama3.1", tools=tools)
    # math_response = await agent.ainvoke(
    #     {"messages": [{"role": "user", "content": "What is (3 + 5) * 10 ?"}]}
    # )
    # print(math_response)
    weather_response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "What is the weather in New York?"}]}
    )
    print(weather_response["messages"][-1].content_blocks)


if __name__ == "__main__":
    asyncio.run(main())
