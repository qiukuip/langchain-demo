import asyncio

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.mcp import MCPAdapter
from langchain_core.messages import AIMessage, ToolMessage

load_dotenv()


async def main():
    async with MCPAdapter("http://localhost:8001/mcp") as adapter:
        tools = await adapter.list_tools()
        for tool in tools:
            print(f"Tool: {tool.name} => Description: {tool.description}")

        agent = create_agent(
            model="ollama:llama3.1",
            tools=tools,
        )
        response = await agent.ainvoke(
            {"messages": [{"role": "user", "content": "What's the weather is SF?"}]}
        )

        total_usage = {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0
        }

        for message in response["messages"]:
            if isinstance(message, AIMessage) and message.usage_metadata is not None:
                for key in total_usage:
                    total_usage[key] += message.usage_metadata[key]
        print("===== token usage =====")
        print(f"input_tokens: {total_usage['input_tokens']}, "
              f"output_tokens: {total_usage['output_tokens']}, "
              f"total_tokens: {total_usage['total_tokens']}")

        print("===== response message =====")
        print(response["messages"][-1].content_blocks)


if __name__ == "__main__":
    asyncio.run(main())
