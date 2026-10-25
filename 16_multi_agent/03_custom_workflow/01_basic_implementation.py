from langchain.agents import create_agent
from langgraph.graph import StateGraph, START, END
from langsmith import BaseModel


class CustomAgent(BaseModel):
    some_property: str


agent = create_agent(
    model="ollama:llama3.1",
    tools=[],
    middleware=[]
)


def agent_node(state: CustomAgent) -> dict:
    """A LangGraph node that invokes a LangChain agent."""
    result = agent.invoke({
        "messages": [{"role": "user", "content": state["query"]}]
    })
    return {"answer": result["messages"][-1].content}


# Build a simple workflow
workflow = (
    StateGraph(CustomAgent)
    .add_node("agent", agent_node)
    .add_edge(START, "agent")
    .add_edge("agent", END)
    .compile()
)

response = workflow.invoke(CustomAgent(some_property=""))
for message in response["messages"]:
    message.pretty_print()
