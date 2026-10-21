import asyncio

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import ToolErrorMiddleware, ToolRetryMiddleware
from langchain_core.tools import tool
from langgraph.prebuilt.tool_node import ToolCallRequest

load_dotenv()


@tool
def connect_to_database(url: str) -> str | None:
    """Connect to the database"""
    print("connecting to database...")
    if "sqlite://" in url:
        return f"Database connect successfully!"
    raise ConnectionError("Unsupported database url")


@tool
def retry_connection(url: str) -> str | None:
    """Retry the connection"""
    print("retrying connection...")
    if "sqlite://" in url:
        return f"Retry to connect the database successfully!"
    raise ConnectionError("Retry the connection failed")


def on_error(exception: Exception, request: ToolCallRequest) -> str | None:
    if isinstance(exception, ConnectionError):
        return f"{request.tool_call['name']} failed with {type(exception).__name__}: {exception}, fix the input and retry."
    return None


async def aon_error(exception: Exception, request: ToolCallRequest) -> str | None:
    if isinstance(exception, ConnectionError):
        return f"Tool {request.tool_call['name']} encountered a connection error, please try again later."
    return None


agent = create_agent(
    system_prompt="如果 connect_to_database 连接数据失败，请使用 retry_connection 进行重试。",
    model="ollama:llama3.1",
    tools=[connect_to_database, retry_connection],
    middleware=[
        ToolErrorMiddleware(on_error=on_error),
        ToolRetryMiddleware(max_retries=3,
                            backoff_factor=2.0,
                            initial_delay=1.0,
                            on_failure="error",
                            # 用来筛选哪些工具出错时进行重试
                            tools=[connect_to_database]
                            ),
    ]
)
response = asyncio.run(
    agent.ainvoke(
        {"messages": [{"role": "user", "content": "connect to the database: jdbc://localhost:3306"}]}
    )
)
for msg in response["messages"]:
    print(msg.pretty_print())
