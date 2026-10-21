from deepagents import CompiledSubAgent
from deepagents.backends import StateBackend
from deepagents.middleware.subagents import SubAgentMiddleware
from langchain.agents import create_agent
from langgraph.graph import StateGraph
from pydantic import BaseModel


class CustomState(BaseModel):
    pass


def create_weather_graph():
    workflow = StateGraph(state_schema=CustomState)
    return workflow.compile()


weather_graph = create_weather_graph()

weather_subagent = CompiledSubAgent(
    name="weather",
    description="This subagent can get weather in cities.",
    runnable=weather_graph
)

agent = create_agent(
    model="claude-sonnet-4-6",
    middleware=[
        SubAgentMiddleware(
            subagents=[weather_subagent],
            backend=StateBackend()
        )
    ],
)
