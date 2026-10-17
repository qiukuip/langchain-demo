from typing import Any

from langchain.agents import create_agent
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolRuntime
from langgraph.types import interrupt
from pydantic import BaseModel


class MemoryPutInput(BaseModel):
    key: str
    value: Any


class MemoryGetInput(BaseModel):
    key: str


class GeolocationGetInput(BaseModel):
    save: bool = True


def _interrupt_for_client(
        tool_name: str,
        args: dict[str, Any],
        runtime: ToolRuntime
) -> Any:
    return interrupt({
        "type": "tool",
        "tool_call": {
            "id": runtime.tool_call_id,
            "name": tool_name,
            "args": args,
        }
    })


@tool("memory_put", description="Store a memory in the user's browser", args_schema=MemoryPutInput)
def memory_put(key: str, value: Any, runtime: ToolRuntime) -> Any:
    return _interrupt_for_client("memory_put", {"key": key, "value": value}, runtime)


@tool("memory_get", description="Retrieve a memory in the user's browser", args_schema=MemoryGetInput)
def memory_get(key: str, runtime: ToolRuntime) -> Any:
    return _interrupt_for_client("memory_get", {"key": key}, runtime)

@tool(
    "geolocation_get",
    description="Get the user's current location from the browser.",
    args_schema=GeolocationGetInput,
)
def geolocation_get(runtime: ToolRuntime, save: bool = True) -> Any:
    return _interrupt_for_client(
        "geolocation_get",
        {"save": save},
        runtime,
    )

agent = create_agent(
    model="openai:gpt-5.5",
    tools=[memory_put, memory_get, geolocation_get],
    checkpointer=MemorySaver(),
)
