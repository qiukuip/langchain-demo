import asyncio

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

load_dotenv()


async def main():
    client = MultiServerMCPClient(
        {
            "weather": {
                "transport": "streamable_http",
                "url": "http://localhost:8000/mcp",
            }
        }
    )

    async with client.session("weather") as session:
        tools = await load_mcp_tools(session)
        agent = create_agent(model="google_genai:gemini-3.1-flash-lite", tools=tools)
        result1 = await agent.ainvoke(
            {"messages": [HumanMessage(content="What is the weather in New York?")]}
        )
        print(result1)

        print("=====")

        result2 = await agent.ainvoke(
            {"messages": [HumanMessage(content="and Chicago?")]}
        )
        print(result2)


if __name__ == "__main__":
    asyncio.run(main())
