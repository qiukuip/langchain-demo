from langchain.tools import ToolRuntime, tool
from langchain_core.messages import ToolMessage
from langgraph.types import Command


@tool
def set_language(country: str, runtime: ToolRuntime) -> Command:
    """Set the language for the conversation based on country."""
    language = None
    if country == "CN":
        language = "zh-CN"
    else:
        language = "en-US"
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

