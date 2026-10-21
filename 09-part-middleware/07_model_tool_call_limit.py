from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import ModelCallLimitMiddleware, ToolCallLimitMiddleware
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

agent = create_agent(
    model="ollama:ollama3.1",
    tools=[],
    middleware=[
        ModelCallLimitMiddleware(thread_limit=5, run_limit=3, exit_behavior="end"),
        ToolCallLimitMiddleware(tool_name="web_search", thread_limit=5, run_limit=3),
        ToolCallLimitMiddleware(tool_name="query_database", thread_limit=10),

    ],
    checkpointer=InMemorySaver()
)
