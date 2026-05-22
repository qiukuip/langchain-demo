from typing import Literal

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain.messages import AIMessage, AIMessageChunk, AnyMessage, ToolMessage
from pydantic import BaseModel, Field

load_dotenv()


class MeetingAction(BaseModel):
    """Action items extracted from a meeting transcript"""

    task: str = Field(description="The specific task to be completed")
    assignee: str = Field(description="Person responsible for the task")
    priority: Literal["Low", "Medium", "High"] = Field(description="Priority level")


def _render_message_chunk(token: AIMessageChunk) -> None:
    if token.text:
        print(token.text, end="|")
    if token.tool_call_chunks:
        print(token.tool_call_chunks)


def _render_completed_message(message: AnyMessage) -> None:
    if isinstance(message, AIMessage) and message.tool_calls:
        print(f"Tool call: {message.tool_calls}")
    if isinstance(message, ToolMessage):
        print(f"Tool response: {message.content_blocks}")


agent = create_agent(
    model="google_genai:gemini-3.1-flash-lite",
    response_format=ToolStrategy(
        schema=MeetingAction,
        tool_message_content="Action item captured and added to meeting notes!",
    ),
)
input_message = {
    "role": "user",
    "content": "From out meeting, Sarah needs to update project time line as soon as possible",
}
for chunk in agent.stream(
    {"messages": [input_message]}, stream_mode=["messages", "updates"], version="v2"
):
    if chunk["type"] == "messages":
        token, metadata = chunk["data"]
        if isinstance(token, AIMessageChunk):
            _render_message_chunk(token)
    elif chunk["type"] == "updates":
        for source, update in chunk["data"].items():
            if source in ("model", "tools"):
                _render_completed_message(update["messages"][-1])
