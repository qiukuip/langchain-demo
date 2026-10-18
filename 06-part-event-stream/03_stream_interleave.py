from dotenv import load_dotenv
from langchain.agents import create_agent, AgentState
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.prebuilt import ToolRuntime
from langgraph.prebuilt._tool_call_transformer import ToolCallTransformer

load_dotenv()


class CustomAgentState(AgentState):
    user_id: str


@tool
def query_user_name(runtime: ToolRuntime[CustomAgentState]) -> str:
    """Query the current user's name."""
    user_id = runtime.state["user_id"]
    return "John" if user_id == "u001" else "unknown user"


agent = create_agent(
    model="google_genai:gemini-3.1-flash-lite",
    tools=[query_user_name],
    state_schema=CustomAgentState
)
stream = agent.stream_events(
    {
        "messages": [HumanMessage(content="What's my username?")],
        "user_id": "u001",
    },
    version="v3",
    transformers=[ToolCallTransformer],
)
for name, item in stream.interleave("messages", "tool_calls", "values"):
    if name == "messages":
        print(item.text)
    elif name == "tool_calls":
        print(f"{item.tool_name}: {item.input}")
    elif name == "values":
        print(item)
