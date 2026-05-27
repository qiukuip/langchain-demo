from typing import Literal, NotRequired

from langchain.agents import AgentState, create_agent
from langchain.messages import AIMessage, ToolMessage
from langchain.tools import ToolRuntime, tool
from langgraph.constants import END, START
from langgraph.graph.state import StateGraph
from langgraph.types import Command


class MultiAgentState(AgentState):
    active_agent: NotRequired[str]


@tool
def transfer_to_sales(runtime: ToolRuntime) -> Command:
    """Transfer to the sales agent."""
    last_ai_message = next(
        msg for msg in reversed(runtime.state["messages"]) if isinstance(msg, AIMessage)
    )
    transfer_message = ToolMessage(
        content="Transferred to sales agent from support agent",
        tool_call_id=runtime.tool_call_id,
    )
    return Command(
        goto="sales_agent",
        update={
            "active_agent": "sales_agent",
            "messages": [last_ai_message, transfer_message],
        },
        graph=Command.PARENT,
    )


@tool
def transfer_to_support(runtime: ToolRuntime) -> Command:
    """Transfer to the support agent."""
    last_ai_message = next(
        msg for msg in reversed(runtime.state["messages"]) if isinstance(msg, AIMessage)
    )
    transfer_message = ToolMessage(
        content="Transferred to support agent from sales agent",
        tool_call_id=runtime.tool_call_id,
    )
    return Command(
        goto="support_agent",
        update={
            "active_agent": "support_agent",
            "messages": [last_ai_message, transfer_message],
        },
        graph=Command.PARENT,
    )


sales_agent = create_agent(
    model="google_genai:gemini-3.1-flash-lite",
    tools=[transfer_to_support],
    system_prompt="You are a sales agent. Help with sales inquires. If asked about technical issues or support, transfer to the support agent.",
)
support_agent = create_agent(
    model="google_genai:gemini-3.1-flash-lite",
    tools=[transfer_to_sales],
    system_prompt="You are a support agent. Help with technical issues. If asked about pricing or purchasing, transfer to sales agent.",
)


def call_sales_agent(state: MultiAgentState) -> Command:
    response = sales_agent.invoke(state)
    return response


def call_support_agent(state: MultiAgentState) -> Command:
    response = support_agent.invoke(state)
    return response


def router_after_agent(
    state: MultiAgentState,
) -> Literal["sales_agent", "support_agent", "__end__"] | str:
    """Route based on active agent, or END if the agent finished without handoff."""
    messages = state.get("messages", [])
    if messages:
        last_message = messages[-1]
        if isinstance(last_message, AIMessage) and not last_message.tool_calls:
            return "__end__"
    active = state.get("active_agent", "sales_agent")
    return active if active else "sales_agent"


def route_initial(
    state: MultiAgentState,
) -> Literal["sales_agent", "support_agent"] | str:
    """Route to the active agent based on state, default to sales agent."""
    return state.get("active_agent") or "sales_agent"


app = StateGraph(MultiAgentState)

app.add_node("sales_agent", sales_agent)
app.add_node("support_agent", support_agent)

app.add_conditional_edges(START, route_initial, ["sales_agent", "support_agent"])
app.add_conditional_edges(
    "sales_agent", router_after_agent, ["sales_agent", "support_agent", END]
)
app.add_conditional_edges(
    "support_agent", router_after_agent, ["sales_agent", "support_agent", END]
)

graph = app.compile()

result = graph.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "Hi, I'm having trouble with my account login. Can you help?",
            }
        ]
    }
)
for msg in result["messages"]:
    msg.pretty_print()
