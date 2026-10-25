from dotenv import load_dotenv
from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import after_agent
from langchain.chat_models import init_chat_model
from langchain.tools import ToolRuntime, tool
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import ToolMessage
from langgraph.runtime import Runtime
from langgraph.types import Command

load_dotenv()


class CustomState(AgentState):
    # 主 agent 和子 agent 都声明此字段，才能在各自的状态中保存它。
    example_state_key: str


@after_agent(state_schema=CustomState)
def save_subagent_output(state: CustomState, runtime: Runtime) -> dict:
    """子 agent 完成任务后，将最终回答保存到额外的状态字段。"""
    return {"example_state_key": state["messages"][-1].content}


model: BaseChatModel = init_chat_model(
    model="llama3.1",
    model_provider="ollama",
    temperature=0,
)

subagent1 = create_agent(
    model=model,
    system_prompt=(
        "你是一名技术知识助手，基于已有知识回答问题，用中文简洁说明。"
        "你没有联网搜索工具，不要声称已搜索互联网。"
    ),
    state_schema=CustomState,
    middleware=[save_subagent_output],
)


@tool(
    "subagent1",
    description="Ask the technical knowledge subagent to explain a concept.",
)
def call_subagent1(
        query: str,
        runtime: ToolRuntime,
) -> Command:
    result = subagent1.invoke({
        "messages": [{"role": "user", "content": query}]
    })
    # 子 agent 的状态不会自动合并到主 agent，需要显式回传所需字段。
    return Command(
        update={
            "example_state_key": result["example_state_key"],
            "messages": [
                # 必须匹配主 agent 发起的工具调用 ID，让它能继续生成回答。
                ToolMessage(
                    content=result["messages"][-1].content,
                    tool_call_id=runtime.tool_call_id
                )
            ]
        }
    )


main_agent = create_agent(
    model=model,
    tools=[call_subagent1],
    state_schema=CustomState,
    system_prompt=(
        "你是协调助手。遇到技术概念问题时，先调用一次 subagent1 工具，"
        "再根据工具返回的结果用中文回答用户。"
    ),
)

if __name__ == "__main__":
    response = main_agent.invoke({
        "messages": [{"role": "user", "content": "请解释什么是子 agent。"}],
        "example_state_key": "",
    })
    print("===== 主 agent 最终回答 =====")
    print(response["messages"][-1].content)
    print("===== 子 agent 回传的状态 =====")
    print(response["example_state_key"])
