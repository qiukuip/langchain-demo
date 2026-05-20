from langchain.agents import AgentState, create_agent
from langchain_core.messages import ToolMessage
from langgraph.types import Command
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain.tools import ToolRuntime, tool


class CustomState(AgentState):
    username: str


class CustomContext(BaseModel):
    user_id: str


@tool
def update_user_info(runtime: ToolRuntime[CustomContext, CustomState]) -> Command:
    """Update user information"""
    user_id = runtime.context.user_id
    name = "John Smith" if user_id == "abc123" else "Unknown user"
    return Command(
        update={
            "username": name,
            "messages": [
                ToolMessage(
                    content="Successfully update user information",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )


@tool
def greet(runtime: ToolRuntime[CustomContext, CustomState]) -> str | Command:
    """Use this to greet the user if you found their info"""
    username = runtime.state.get("username", None)
    if username is None:
        return Command(
            update={
                "username": username,
                "messages": [
                    ToolMessage(
                        content="Please call the 'update_user_info' tool it will get and update the user's name",
                        tool_call_id=runtime.tool_call_id,
                    )
                ],
            }
        )
    else:
        return f"Hello {username}!"


load_dotenv()

agent = create_agent(
    model="google_genai:gemini-3.1-flash-lite",
    tools=[update_user_info, greet],
    state_schema=CustomState,
    context_schema=CustomContext,
)
response = agent.invoke(
    {
        "messages": [{"role": "user", "content": "greet the user"}],
    },
    context=CustomContext(user_id="abc123"),
)
print(response["messages"][-1].content)
