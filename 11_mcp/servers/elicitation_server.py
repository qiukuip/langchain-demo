from os import name, path
from mcp.server.fastmcp import Context, FastMCP
from pydantic import BaseModel

server = FastMCP(name="Profile", host="0.0.0.0", port=8001)


class UserDetails(BaseModel):
    email: str
    age: int


@server.tool()
async def create_profile(name: str, ctx: Context) -> str:
    """Create a user profile, requesting details via elicitation"""
    result = await ctx.elicit(
        message=f"Please provide details for {name}'s profile:", schema=UserDetails
    )
    if result.action == "accept" and result.data:
        return f"Create profile for {name}: email={result.data.email}, age={result.data.age}"
    if result.action == "decline":
        return f"User declined. Created minimal profile for {name}."
    return "Profile creation cancelled."


if __name__ == "__main__":
    server.run(transport="streamable-http")
