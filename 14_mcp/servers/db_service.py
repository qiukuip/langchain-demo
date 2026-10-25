from fastmcp import FastMCP

mcp = FastMCP(name="User Service")

tags = {"Database", "User Service"}
meta = {
    "category": "Database",
    "version": "1.0.0"
}

USER_INFO = [
    {
        "id": 1,
        "name": "Alice",
        "gender": "Male",
        "email": "alice@happ.com"
    }
]


@mcp.tool(
    name="SaveUserInfo",
    version="1.0.0",
    title="Save user info",
    description="Save user information to database.",
    tags=tags,
    meta=meta
)
async def save_user_info(user_info: dict) -> str:
    """Save user information to database."""
    max_user_id = 1
    for user in USER_INFO:
        user_id = int(user["id"])
        if user_id > max_user_id:
            max_user_id = user_id
    user_info["user_id"] = max_user_id
    USER_INFO.append(user_info)
    return f"User {max_user_id}'s info saved successfully."


@mcp.tool(
    name="QueryUserInfo",
    version="1.0.0",
    title="Query user info",
    description="Query user information from database.",
    tags=tags,
    meta=meta
)
async def query_user_info(user_id: int) -> dict | str:
    """Query user information from database."""
    for user in USER_INFO:
        if user["id"] == user_id:
            return user
    return f"User {user_id} doesn't exist."


@mcp.tool(
    name="UpdateUserInfo",
    version="1.0.0",
    title="Update user info",
    description="Update user information from database.",
    tags=tags,
    meta=meta
)
async def update_user_info(user_info: dict) -> str:
    """Update user information from database."""
    if user_info is None or user_info["id"] is None:
        raise ValueError("user_info must not be None")
    for user in USER_INFO:
        if user["id"] == user_info["id"]:
            USER_INFO.remove(user)
            break
    USER_INFO.append(user_info)
    return f"User {user_info['user_id']}'s info updated successfully."


@mcp.tool(
    name="DeleteUserInfo",
    version="1.0.0",
    title="Delete user info",
    description="Delete user information from database by user_id.",
    tags=tags,
    meta=meta
)
async def delete_user_info(user_id: str) -> str:
    """Delete user information from database by user_id."""
    for user in USER_INFO:
        if user["id"] != user_id:
            USER_INFO.remove(user)
            break
    return f"User {user_id}'s info deleted successfully."


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8001)
