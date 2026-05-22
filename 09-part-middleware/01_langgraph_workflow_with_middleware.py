from typing import Any, TypedDict

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langgraph.constants import END, START
from langgraph.graph.state import StateGraph

load_dotenv()


class TextState(TypedDict):
    text: str
    proceed_text: str
    length: int


@tool
def node1_add_exclaimation(state: TextState) -> dict[str, Any]:
    """Append exclaimation to text"""
    print("node1_add_exclaimation running")
    proceed = state["text"] + " - node proceed"
    return {"proceed_text": proceed}


@tool
def node2_count_length(state: TextState) -> dict[str, Any]:
    """Count length of text"""
    print("node2_count_length running")
    length = len(state["proceed_text"])
    return {"length": length}


agent = create_agent(
    model="google_genai:gemini-3.1-flash-lite",
    tools=[node1_add_exclaimation, node2_count_length],
)


graph = (
    StateGraph(TextState)
    .add_node("agent", agent)
    .add_node("add_exclaimamtion", node1_add_exclaimation)
    .add_node("count_length", node2_count_length)
    .add_edge(START, "add_exclaimamtion")
    .add_edge("add_exclaimamtion", "count_length")
    .add_edge("count_length", END)
).compile()
initial_state = {"text": "Hello StateGraph"}
final_state = graph.invoke(initial_state)
print(f"original text: {final_state['text']}")
print(f"proceed_text: {final_state['proceed_text']}")
print(f"length: {final_state['length']}")
