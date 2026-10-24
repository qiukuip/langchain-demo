from fastmcp import FastMCP, Context
from mcp.types import ElicitRequest, ElicitRequestFormParams, ElicitResult, InputRequiredResult
from pydantic import BaseModel

server = FastMCP(name="Profile")


class UserDetails(BaseModel):
    email: str
    age: int


@server.tool(
    description="Profile creation",
)
async def create_profile(name: str, ctx: Context) -> str | InputRequiredResult:
    """Create a user profile, requesting details via elicitation."""
    # 恢复时工具会重新执行，因此请求 key 必须稳定，实际操作放在收到答案之后。
    request_key = "profile_details"
    responses = ctx.input_responses or {}
    if request_key not in responses:
        return InputRequiredResult(
            input_requests={
                request_key: ElicitRequest(
                    params=ElicitRequestFormParams(
                        message=f"Please provide details for {name}'s profile:",
                        requested_schema=UserDetails.model_json_schema(),
                    ),
                    method="elicitation/create",
                )
            }
        )

    result = responses[request_key]
    if not isinstance(result, ElicitResult):
        raise ValueError("Expected an elicitation response for profile details.")
    if result.action == "accept":
        details = UserDetails.model_validate(result.content)
        return f"Create profile for {name}: email={details.email}, age={details.age}"
    if result.action == "decline":
        return f"User declined. Created minimal profile for {name}."
    return "Profile creation cancelled."


if __name__ == "__main__":
    server.run(transport="streamable-http", host="0.0.0.0", port=8000)
