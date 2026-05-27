from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.prompts import load_mcp_prompt


async def main():
    client = MultiServerMCPClient(
        {
            "math": {
                "command": "python",
                "transport": "stdio",
                "args": ["11_mcp/servers/math_server.py"],
            }
        }
    )
    async with client.session("math") as session:
        tools = await client.get_tools()
        messages1 = await client.get_prompt("math", "summarize")
        messages2 = await client.get_prompt(
            "server_name",
            "code_review",
            arguments={"language": "python", "focus": "security"},
        )
        messages3 = await load_mcp_prompt(session, "summarize")
        messages4 = await load_mcp_prompt(
            session,
            "code_review",
            arguments={"language": "python", "focus": "security"},
        )

        for message in messages1:
            print(f"Message Type: {message.type}")
            print(f"Message Content: {message.content}")
