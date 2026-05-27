from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, ToolMessage
from langchain.tools import tool
from langgraph.constants import END, START
from langgraph.graph.message import add_messages
from langgraph.graph.state import StateGraph

load_dotenv()

sub_agent = create_agent(model="google_genai:gemini-3.1-flash-lite", tools=[])


@tool("search_market_news", description="Search market news")
def search_market_news(company: str) -> str:
    """搜索特定公司或行业的最新市场新闻和动态"""
    return f"[市场搜索结果] 关于 {company} 的最新动态显示，该公司上季度营收增长了 15%，并在 AI 领域发布了新产品。"


@tool("query_internel_sales_db", description="Query internal sales DB")
def query_internel_sales_db(department: str) -> str:
    """查询公司内部指定部门的销售数据表"""
    mock_db = {
        "销售部": "Q1 销售额 500 万，Q2 销售额 600 万",
        "技术部": "研发投入占比超 120%",
    }
    return f"[内部数据库结果] {department} 的数据为 -> {mock_db.get(department, '未找到该部门数据')}"


def create_sub_agent(tools, system_prompt):
    """快速创建带有特定工具和提示词的子代理节点"""
    model = init_chat_model(
        model="gemini-3.1-flash-lite", model_provider="google_genai", temperature=0.7
    )
    model.bind_tools(tools=tools)

    def sub_agent_node(state):
        messages = [{"role": "system", "content": system_prompt}] + state["messages"]
        response = model.invoke(messages)
        if response.tool_calls:
            tool_map = {tool.name: tool for tool in response.tool_calls}
            tool_results = []
            for tool_call in response.tool_calls:
                selected_tool = tool_map[tool_call["name"]]
                result = selected_tool.invoke(tool_call["args"])
                tool_results.append(
                    ToolMessage(content=result, tool_call_id=tool_call["id"])
                )
            return {"messages": [response] + tool_results}
        return {"messages": [response]}

    return sub_agent_node


market_agent = create_sub_agent(
    tools=[search_market_news],
    system_prompt="你是一个专业的市场分析师，只负责使用工具搜索外部市场新闻，请务必使用提供的工具。",
)
data_agent = create_sub_agent(
    tools=[query_internel_sales_db],
    system_prompt="你是一个严谨的内部数据专员，只负责查询公司内部的数据库，请务必使用提供的内部数据查询工具。",
)


class State(TypedDict):
    messages: Annotated[list, add_messages]
    next_node: str


def router_node(state):
    user_input = state["messages"][-1].content
    if "市场" in user_input or "新闻" in user_input:
        return {"next_node": "market_agent"}
    elif "内部" in user_input or "销售" in user_input:
        return {"next_node": "data_agent"}
    else:
        return {"next_node": "END"}


workflow = StateGraph(State)

workflow.add_node("market_agent", market_agent)
workflow.add_node("data_agent", data_agent)
workflow.add_node("router", router_node)

workflow.add_edge(START, "router")
workflow.add_conditional_edges(
    "router", lambda x: x["next_node"], ["market_agent", "data_agent", END]
)
workflow.add_edge("market_agent", END)
workflow.add_edge("data_agent", END)

app = workflow.compile()

if __name__ == "__main__":
    print("===== 测试子代理 A: 市场调研 =====")
    inputs = {"messages": [HumanMessage("帮我查一下火星有哦科技最近的市场新闻")]}
    for chunk in app.stream(inputs):
        for key, val in chunk.items():
            print(f"执行节点: {key}")
            if "messages" in val:
                print(val["messages"][-1].content)

    print("===== 测试子代理 B: 内部数据 =====")
    inputs = {"messages": [HumanMessage("查一下2025年销售售部的业绩数据")]}
    for chunk in app.stream(inputs):
        for key, val in chunk.items():
            print(f"执行节点: {key}")
            if "messages" in val:
                print(val["messages"][-1].content)
