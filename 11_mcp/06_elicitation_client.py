import asyncio

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.messages import HumanMessage, SystemMessage
from langchain_mcp_adapters.callbacks import CallbackContext
from langchain_mcp_adapters.client import Callbacks, MultiServerMCPClient
from mcp.shared.context import RequestContext
from mcp.types import ElicitRequestParams, ElicitResult


async def on_elicitation(
    mcp_context: RequestContext, params: ElicitRequestParams, context: CallbackContext
) -> ElicitResult:
    """Handle elicitation requests from MCP servers"""
    print(f"Model need more information: {params.message}")
    print(f"Model need params: {params}")
    return ElicitResult(action="accept", content={"email": "user@gmail.com", "age": 20})


async def main():
    client = MultiServerMCPClient(
        {
            "profile": {
                "transport": "streamable_http",
                "url": "http://localhost:8001/mcp",
            }
        },
        callbacks=Callbacks(on_elicitation=on_elicitation),
    )
    async with client.session("profile") as session:
        load_dotenv()
        tools = await client.get_tools()
        agent = create_agent(model="google_genai:gemini-3.1-flash-lite", tools=tools)
        result = await agent.ainvoke(
            {
                "messages": [
                    SystemMessage(
                        "You are a helpful assistant, help user to create a profile. Request more detail information to user if needed."
                    ),
                    HumanMessage("Create a profile for me, my name is Alice."),
                ]
            }
        )
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
