import asyncio

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()


async def main():
    client = MultiServerMCPClient(
        {
            "langchain_docs_server": {
                "url": "https://docs.langchain.com/mcp",
                "transport": "http"
            }
        }
    )
    tools = await client.get_tools()
    agent = create_agent(
        model="google_genai:gemini-3.1-flash-lite",
        tools=tools,
    )
    result = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "如何给 Agent 添加短期记忆？"
                }
            ]
        }
    )
    print(result["messages"][-1].content_blocks)


if __name__ == "__main__":
    asyncio.run(main())
