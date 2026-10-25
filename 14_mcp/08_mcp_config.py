import asyncio

from fastmcp import ClientGroup, Client
from langchain.agents import create_agent
from langchain.mcp import MCPAdapter
from langchain_core.messages import HumanMessage

MCP_SERVER_CONFIG = {
    "calculator": {
        "name": "calculator",
        "command": "python",
        "args": ["servers/math_server.py"]
    },
    "user_service": {
        "name": "user_service",
        "transport": "streamable-http",
        "url": "http://localhost:8001/mcp"
    }
}


async def fleet_agent(config):
    async with MCPAdapter(MCP_SERVER_CONFIG) as mcp:
        tools = await mcp.list_tools()
        for tool in tools:
            print(f"Found tool: {tool.name}")
            print(f"\t{tool.description}")
            print("\n")
        print("=====\n")

        agent = create_agent(
            model="ollama:llama3.1",
            tools=tools
        )
        return agent


async def agent_from_group():
    group = ClientGroup(
        clients={
            "user_service": Client(transport="streamable-http", url="http://localhost:8001/mcp"),
            "calculator": Client(transport="stdio", command="python", args=["servers/calculator.py"], mode="auto")
        }
    )
    async with MCPAdapter(group) as mcp:
        tools = await mcp.list_tools()
        for tool in tools:
            print(f"Found tool: {tool.name}")
            print(f"\t{tool.description}")
            print("\n")
        print("=====\n")

        agent = create_agent(
            model="ollama:llama3.1",
            tools=tools
        )
        return agent


async def main():
    agent = await fleet_agent(MCP_SERVER_CONFIG)
    messages = [HumanMessage(content="Query the user information of user_id: 1 for me.")]
    response = await agent.ainvoke(
        {"messages": messages}
    )
    for message in response["messages"]:
        print(message.pretty_print())


if __name__ == "__main__":
    asyncio.run(main())
