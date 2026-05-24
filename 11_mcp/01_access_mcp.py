import asyncio

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient


async def main():
    client = MultiServerMCPClient(
        {
            "math": {
                "transport": "stdio",
                "command": "python",
                "args": ["11_mcp/servers/math_server.py"],
            },
            "weather": {
                "transport": "streamable_http",
                "url": "http://localhost:8000/mcp",
                "headers": {
                    "Authorization": "Bearer custom_token",
                    "X-Custom-Header": "Custom-Header-Value",
                },
            },
        }
    )

    tools = await client.get_tools()
    load_dotenv()
    agent = create_agent(model="google_genai:gemini-3.1-flash-lite", tools=tools)
    # math_response = await agent.ainvoke(
    #     {"messages": [{"role": "user", "content": "What is (3 + 5) * 10 ?"}]}
    # )
    # print(math_response)
    weather_response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "What is the weather in New York?"}]}
    )
    print(weather_response)


if __name__ == "__main__":
    asyncio.run(main())
