import asyncio

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.mcp import MCPAdapter
from langchain_core.messages import HumanMessage, ToolMessage

load_dotenv()


async def main():
    async with MCPAdapter("http://localhost:8001/mcp") as mcp:
        tools = await mcp.list_tools()
        for tool in tools:
            print(f"Found tool: {tool.name} => {tool.description}")

        agent = create_agent(
            model="ollama:llama3.1",
            tools=tools
        )
        response = await agent.ainvoke(
            {"messages": [HumanMessage("What's the weather in Osaka?")]}
        )

        print("===== response =====")
        for message in response["messages"]:
            if isinstance(message, ToolMessage) and message.status == "error":
                print(f"Tool reported: {message.text}")

        print("===== others =====")
        for message in response["messages"]:
            if isinstance(message, ToolMessage) and message.artifact is not None:
                print(f"Artifact: {message.artifact['structured_content']}")
            for block in message.content_blocks:
                print(f"Message Block Type: {block['type']}")
                if block["type"] == "text":
                    print(f"Text: {block['text']}")
                elif block["type"] == "tool_call":
                    print(f"Tool {block['name']}: {block['args']}")


if __name__ == "__main__":
    asyncio.run(main())
