import asyncio

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.mcp import MCPAdapter
from langchain_core.messages import HumanMessage

load_dotenv()

USER_SERVICE_MCP = "http://localhost:8001/mcp"


async def build_agent(mcp_server):
    async with MCPAdapter(mcp_server) as mcp:
        tools = await mcp.list_tools()
        for tool in tools:
            print(f"Found tool: {tool.name}")
            print(f"\t{tool.description}\n")
        print("======\n")

        agent = create_agent(
            model="ollama:llama3.1",
            tools=tools
        )
        return agent


async def main():
    agent = await build_agent(USER_SERVICE_MCP)
    messages = [HumanMessage(content="Save user info: name is Bob, sex is Female and age is 20.")]
    response1 = await agent.ainvoke({
        "messages": messages
    })
    print(response1["messages"][-1].content_blocks)
    print("=====\n")


if __name__ == "__main__":
    asyncio.run(main())
