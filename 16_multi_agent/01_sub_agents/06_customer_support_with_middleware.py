from typing import Callable

from dotenv import load_dotenv
from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import ModelRequest, ModelResponse, wrap_model_call
from langchain.messages import HumanMessage, ToolMessage
from langchain.tools import ToolRuntime, tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command


class SupportState(AgentState):
    """Track which step is currently active."""

    current_step: str
    warrantty_status: str


@tool
def record_warrantty_status(
    status: str, runtime: ToolRuntime[None, SupportState]
) -> Command:
    """Record warrantty status and transfer to next step."""
    return Command(
        update={
            "messages": [
                ToolMessage(
                    content=f"Warrantty status recorded: {status}",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
            "warrantty_status": status,
            "current_step": "specialist",
        }
    )


@tool
def provide_solutions(runtime: ToolRuntime) -> str:
    """Provide solutions."""
    return "Fix it!"


@wrap_model_call
def apply_step_config(
    request: ModelRequest, handler: Callable[[ModelRequest], ModelResponse]
) -> ModelResponse:
    """Configure agent behivor based on current step."""
    step = request.state.get("current_step", "triage")

    configs = {
        "triage": {
            "prompt": "Collect warrantty information.",
            "tools": [record_warrantty_status],
        },
        "specialist": {
            "prompt": "Provide solutions based on warrantty: {warrantty_status}",
            "tools": [provide_solutions],
        },
    }

    config = configs[step]
    modified_request = request.override(
        system_message=config["prompt"], tools=config["tools"]
    )
    return handler(modified_request)


load_dotenv()
agent = create_agent(
    model="google_genai:gemini-3.1-flash-lite",
    tools=[record_warrantty_status, provide_solutions],
    state_schema=SupportState,
    middleware=[apply_step_config],
    checkpointer=InMemorySaver(),
    system_prompt="You are a helpful assistant. Use provided tools to triage information and  record warrantty status and transfer to next step when need to ",
)
result = agent.invoke(
    {
        "messages": [HumanMessage("My phone was broken")],
        "current_step": "triage",
        "warrantty_status": "It is still in warrantty",
    },
    config={"configurable": {"thread_id": "13-02-01"}},
)
print(result)
