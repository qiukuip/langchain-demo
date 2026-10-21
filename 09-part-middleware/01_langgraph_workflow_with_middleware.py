from typing import Any, TypedDict

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.constants import END, START
from langgraph.graph.state import StateGraph

load_dotenv()


class TextState(TypedDict):
    text: str
    proceed_text: str
    length: int


def node1_add_exclaim(state: TextState) -> dict[str, Any]:
    """Append exclaim to text"""
    print("node1_add_exclaim running")
    proceed = state["text"] + " - node proceed"
    return {"proceed_text": proceed}


def node2_count_length(state: TextState) -> dict[str, Any]:
    """Count length of text"""
    print("node2_count_length running")
    length = len(state["proceed_text"])
    return {"length": length}


agent = create_agent(
    model="ollama:llama3.1",
    tools=[node1_add_exclaim, node2_count_length],
    middleware=[HumanInTheLoopMiddleware(
        interrupt_on={
            "node2_count_length": True,
        }
    )]
)

graph = (
    StateGraph(TextState)
    .add_node("agent", agent)
    .add_node("add_exclaim", node1_add_exclaim)
    .add_node("count_length", node2_count_length)
    .add_edge(START, "add_exclaim")
    .add_edge("add_exclaim", "count_length")
    .add_edge("count_length", END)
    .compile()
)
initial_state = {"text": "Hello StateGraph"}
final_state = graph.invoke(initial_state)
print(f"original text: {final_state['text']}")
print(f"proceed_text: {final_state['proceed_text']}")
print(f"length: {final_state['length']}")
