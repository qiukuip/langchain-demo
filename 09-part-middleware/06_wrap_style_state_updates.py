from typing import Callable

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import (
    AgentState,
    ExtendedModelResponse,
    ModelRequest,
    ModelResponse,
    wrap_model_call,
)
from langgraph.types import Command
from typing_extensions import NotRequired


class UsageTrackingState(AgentState):
    """Agent state with token usage tracking."""

    last_model_call_tokens: NotRequired[int]


@wrap_model_call(state_schema=UsageTrackingState)
def track_usage(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse],
) -> ExtendedModelResponse:
    response = handler(request)
    return ExtendedModelResponse(
        model_response=response,
        command=Command(update={"last_model_call_tokens": 150}),
    )


load_dotenv()
agent = create_agent(
    model="google_genai:gemini-3.1-flash-lite", tools=[], middleware=[track_usage]
)
input_message = {"role": "user", "content": "狸花猫是一个品种吗？"}
result = agent.invoke({"messages": [input_message]})
print(result)
