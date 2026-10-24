from sys import version
from typing import Any
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain.messages import HumanMessage, SystemMessage
from langchain.tools import ToolRuntime, tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.state import RunnableConfig
from langgraph.types import Command
from pydantic_core.core_schema import float_schema


@tool
def write_file(runtime: ToolRuntime) -> str:
    """Write content to local file."""
    return "Content has been saved to local file"


@tool
def execute_sql(runtime: ToolRuntime) -> str:
    """Execute SQL when need to query database."""
    return "Executed SQL successfully."


@tool
def read_data(runtime: ToolRuntime) -> str:
    """Read content from file."""
    return "--> Content from file <--"


load_dotenv()
agent = create_agent(
    model="google_genai:gemini-3.1-flash-lite",
    tools=[write_file, execute_sql, read_data],
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "write_file": True,  # All decisions (approve, edit, reject, respond) alllowed
                "execute_sql": {
                    "allowed_decisions": ["approve", "reject"]  # No edition allowed
                },
                "read_data": False,  # No approval needed
            },
            description_prefix="Tool execution pending approval",
        )
    ],
    checkpointer=InMemorySaver(),
)

system_message = SystemMessage(
    "You are a helpful assistant. Important: when you need to write file or execute sql or read data, you must use the tools provided."
)
human_message1 = HumanMessage("Delete all user from the database.")
config: RunnableConfig = {"configurable": {"thread_id": "1201"}}
# result1 = agent.invoke(
#     {"messages": [system_message, human_message1]},
#     config=config,
#     version="v2",
# )
# print(result1.interrupts)
#
# print("=====")
#
# result2 = agent.invoke(
#     Command(resume={"decisions": [{"type": "approve"}]}), config=config, version="v2"
# )
# print(result2)
#
# print("=====")
#
# result3 = agent.invoke(
#     Command(
#         resume={
#             "decisions": [
#                 {"type": "reject", "message": "This action is not allowed!"}
#             ]
#         }
#     ),
#     config=config,
#     version="v2",
# )
# print(result3)

for chunk in agent.stream(
    {"messages": [system_message, human_message1]},
    stream_mode=["updates", "messages"],
    config=config,
    version="v2",
):
    if chunk["type"] == "messages":
        token, metadata = chunk["data"]
        if token.content:
            print(token.content, end="|", flush=True)
    elif chunk["type"] == "updates":
        if "__interrupt__" in chunk["data"]:
            print(f"\n\nInterrupt: {chunk['data']['__interrupt__']}")

print("=====")

for chunk in agent.stream(
    Command(resume={"decisions": [{"type": "approve"}]}),
    stream_mode=["messages"],
    config=config,
    version="v2",
):
    if chunk["type"] == "messages":
        token, metadata = chunk["data"]
        if token.content:
            print(token.content, end="|", flush=True)
