from dataclasses import dataclass

from dotenv import load_dotenv
from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest, before_model, after_model
from langchain_core.messages import HumanMessage
from langgraph.runtime import Runtime

load_dotenv()


@dataclass
class Context:
    username: str


@dynamic_prompt
def dynamic_system_prompt(request: ModelRequest) -> str:
    username = request.runtime.context.username
    system_prompt = f"You are a helpful assistant. Address the user as {username}!"
    return system_prompt


@before_model
def before_model(state: AgentState, runtime: Runtime) -> dict | None:
    print(f"Processing request for user: {runtime.context.username}")
    return None


@before_model
def before_model1(state: AgentState, runtime: Runtime) -> dict | None:
    """Block unauthenticated users when running on LangGraph Server."""
    server = runtime.server_info
    if server is not None and server.user is None:
        raise ValueError("Authentication required")
    print(f"Thread: {runtime.execution_info.thread_id}")
    return None


@after_model
def after_model(state: AgentState, runtime: Runtime) -> dict | None:
    print(f"Completed request for user: {runtime.context.username}")
    return None


agent = create_agent(
    model="ollama:llama3.1",
    middleware=[dynamic_system_prompt, before_model, after_model],
    context_schema=Context
)

response = agent.invoke(
    {"messages": [HumanMessage(content="What's my name?")]},
    context=Context(username="John"),
)
print(response["messages"][-1].content_blocks)
