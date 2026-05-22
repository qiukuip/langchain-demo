from typing import Any, Literal

from dotenv import load_dotenv
from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import after_model
from langchain.chat_models import init_chat_model
from langchain.messages import AIMessage, AIMessageChunk, AnyMessage, ToolMessage
from langchain.tools import tool
from langgraph.config import get_stream_writer
from langgraph.runtime import Runtime
from pydantic import BaseModel, Field

load_dotenv()


class ResponseSafety(BaseModel):
    """Evalate a response as safe or unsafe."""

    evaluation: Literal["safe", "unsafe"] = Field(
        description="Evaluate a response, must select 'safe' or 'unsafe'"
    )


satefy_model = init_chat_model(model="google_genai:gemini-3.1-flash-lite")


@after_model(can_jump_to=["end"])
def safety_guardrail(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    """Model-based guradrail: Use an LLM to evaluate response safety"""
    if not state["messages"]:
        return None

    last_message = state["messages"][-1]
    if not isinstance(last_message, AIMessage):
        return None

    model_with_tools = satefy_model.bind_tools([ResponseSafety], tool_choice="any")
    result = model_with_tools.invoke(
        [
            {
                "role": "system",
                "content": "Evaluate this AI response as generally safe or unsafe.",
            },
            {"role": "user", "content": f"AI response: {last_message.content_blocks}"},
        ]
    )
    stream_writer = get_stream_writer()
    stream_writer(result)

    tool_call = result.tool_calls[0]
    print(f"last_message: {last_message.content_blocks}")
    print(f"tool_call ====> {tool_call}")
    if tool_call["args"]["evaluation"] == "unsafe":
        last_message.content = (
            "I cannot provide that response. Please rephrase your request."
        )
    return None


@tool
def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"


def _render_message_chunk(token: AIMessageChunk) -> None:
    if token.text:
        print(token.text, end="|")
    if token.tool_call_chunks:
        print(token.tool_call_chunks)


def _render_completed_message(message: AnyMessage) -> None:
    if isinstance(message, AIMessage) and message.tool_calls:
        print(f"Tool call: {message.tool_calls}")
    if isinstance(message, ToolMessage):
        print(f"Tool Response: {message.content_blocks}")


input_message = {"role": "user", "content": "What is the weather in Boston?"}
agent = create_agent(
    model="google_genai:gemini-3.1-flash-lite",
    tools=[get_weather],
    middleware=[safety_guardrail],
)
for chunk in agent.stream(
    {"messages": [input_message]},
    stream_mode=["messages", "updates", "custom"],
    version="v2",
):
    if chunk["type"] == "messages":
        token, metadata = chunk["data"]
        if isinstance(token, AIMessageChunk):
            _render_message_chunk(token)
    elif chunk["type"] == "updates":
        for source, update in chunk["data"].items():
            if source in ("model", "tools"):
                _render_completed_message(update["messages"][-1])
    elif chunk["type"] == "custom":
        print(f"Tool calls: {chunk['data'].tool_calls}")
