import asyncio

from dotenv import load_dotenv
from langchain.mcp import MCPAdapter

load_dotenv()


async def main():
    async with MCPAdapter("https://docs.langchain.com/mcp") as adapter:
        tools = await adapter.list_tools()
        for tool in tools:
            print(f"Tool: {tool.name}\n")
            print(f"\tDescription: {tool.description}\n")


if __name__ == "__main__":
    asyncio.run(main())
