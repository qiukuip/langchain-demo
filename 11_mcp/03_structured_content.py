import asyncio

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.messages import ToolMessage
from langchain_mcp_adapters.client import MultiServerMCPClient


async def main():
    client = MultiServerMCPClient(
        {
            "weather": {
                "transport": "streamable_http",
                "url": "http://localhost:8000/mcp",
            }
        },
        tool_interceptors=[],
    )
    tools = await client.get_tools()
    load_dotenv()
    agent = create_agent(model="google_genai:gemini-3.1-flash-lite", tools=tools)
    input_message = {"role": "user", "content": "Get weather information for New York."}
    result = await agent.ainvoke({"messages": [input_message]})
    for message in result["messages"]:
        if isinstance(message, ToolMessage) and message.artifact:
            structured_content = message.artifact["structured_content"]
            print(structured_content)

        print(f"Raw content: {message.content}")

        for block in message.content_blocks:
            if block["type"] == "text":
                print(f"Text: {block.get('text')}")
            elif block["type"] == "image":
                print(f"Image URL: {block.get('url')}")
                print(f"Image Content: {block.get('base64', '')[:50]}")


if __name__ == "__main__":
    asyncio.run(main())
