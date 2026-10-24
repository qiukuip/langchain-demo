from typing import Literal, NotRequired, TypedDict
from dotenv import load_dotenv
from langchain.agents import AgentState, create_agent
from langchain.agents.structured_output import ProviderStrategy
from langchain.messages import AIMessage, ToolMessage
from langchain.tools import ToolRuntime, tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import END, START
from langgraph.graph.state import StateGraph
from langgraph.types import Command
from pydantic import BaseModel, Field


load_dotenv()


class CustomState(AgentState):
    active_agent: Literal["classify_agent", "mathematic_agent", "history_agent"]


class ProblemCategory(BaseModel):
    problem_category: Literal["数学", "历史", "其他"] = Field(description="问题分类")


@tool
def transfer_to_mathematic_agent(runtime: ToolRuntime) -> Command:
    """如果是数学问题则转给数学代理"""
    last_ai_message = next(
        msg for msg in reversed(runtime.state["messages"]) if isinstance(msg, AIMessage)
    )
    tool_message = ToolMessage(
        content="Transfer to mathematic agent", tool_call_id=runtime.tool_call_id
    )
    return Command(
        goto="mathematic_agent",
        update={
            "messages": [last_ai_message, tool_message],
            "active_agent": "mathematic_agent",
        },
        graph=Command.PARENT,
    )


@tool
def transfer_to_history_agent(runtime: ToolRuntime) -> Command:
    """如果是历史问题则转给历史代理"""
    last_ai_message = next(
        msg for msg in reversed(runtime.state["messages"]) if isinstance(msg, AIMessage)
    )
    tool_message = ToolMessage(
        content="Transfer to history agent", tool_call_id=runtime.tool_call_id
    )
    return Command(
        goto="history_agent",
        update={
            "messages": [last_ai_message, tool_message],
            "active_agent": "history_agent",
        },
        graph=Command.PARENT,
    )


def initial_route(
    state: CustomState,
) -> Literal["classify_agent", "mathematic_agent", "history_agent"]:
    """根据状态确定活跃代理，默认使用分类代理"""
    return state.get("active_agent", "classify_agent")


def router_after_agent(
    state: CustomState,
) -> Literal["classify_agent", "mathematic_agent", "history_agent", "__end__"]:
    last_ai_message = next(
        msg for msg in reversed(state["messages"]) if isinstance(msg, AIMessage)
    )
    if "数学" in last_ai_message.content:
        return "mathematic_agent"
    elif "历史" in last_ai_message.content:
        return "history_agent"
    else:
        return "__end__"


classify_agent = create_agent(
    model="google_genai:gemini-3.1-flash-lite",
    tools=[transfer_to_mathematic_agent, transfer_to_history_agent],
    checkpointer=InMemorySaver(),
    system_prompt="你是一个问题分类助手，请对用户的问题进行分类，如果是数学问题则回答“数学”，如果是历史问题则回答“历史”，如果是他类别，则回答“未知”。",
    response_format=ProviderStrategy(ProblemCategory),
)
mathematic_agent = create_agent(
    model="google_genai:gemini-3.1-flash-lite",
    system_prompt="你是一个知识丰富的数学问题助手，尽你所能回答用户的问题。",
)
history_agent = create_agent(
    model="google_genai:gemini-3.1-flash-lite",
    system_prompt="你是一个知识丰富的历史问题助手，尽你所能回答用户的问题。",
)

app = StateGraph(CustomState)

app.add_node("classify_agent", classify_agent)
app.add_node("mathematic_agent", mathematic_agent)
app.add_node("history_agent", history_agent)

app.add_edge(START, "classify_agent")
app.add_conditional_edges(
    "classify_agent", router_after_agent, ["mathematic_agent", "history_agent", END]
)
app.add_edge("mathematic_agent", END)
app.add_edge("history_agent", END)

graph = app.compile()

input_message = {
    "role": "user",
    "content": "证明勾股定理的常用方法有哪些？请简单罗列。",
    # "content": "请问唐、宋、元、明、清这几个朝代各存在了多少年？",
}
config = {"configurable": {"thread_id": "130401"}}
result = graph.invoke({"messages": [input_message]}, config=config, version="v2")
for msg in result["messages"]:
    print(msg.content)
