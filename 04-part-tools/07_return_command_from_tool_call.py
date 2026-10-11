from langchain.tools import ToolRuntime, tool
from langchain_core.messages import ToolMessage
from langgraph.types import Command


@tool
def set_language(country: str, runtime: ToolRuntime) -> Command:
    """Set the language for the conversation based on country."""
    language = "en-US"
    if country == "CN":
        language = "zh-CN"
    return Command(
        update={
            "language": language,
            "messages": [
                ToolMessage(
                    content=f"Language set to {language}",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )
