"""通过 --interrupt-mode batched 或 --interrupt-mode per_call 切换审批模式。"""

import argparse
import json
from typing import Literal

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware, InterruptOnConfig
from langchain.messages import HumanMessage, SystemMessage
from langchain.tools import ToolRuntime, tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt.tool_node import ToolCallRequest
from langgraph.types import Command
from pydantic import ValidationError


@tool
def write_file(content: str, runtime: ToolRuntime) -> str:
    """Write content to local file (mock execution)."""
    return f"Content has been saved to local file: {content}"


@tool
def execute_sql(runtime: ToolRuntime) -> str:
    """Execute SQL when need to query database (mock execution)."""
    return "Executed SQL successfully."


@tool
def read_data(runtime: ToolRuntime) -> str:
    """Read content from file."""
    return "--> Content from file <--"


def is_execute_sql(request: ToolCallRequest) -> bool:
    args = request.tool_call["args"]
    print(f"Args: {args}")
    return request.tool_call["name"] == "execute_sql"


interrupt_on_config_write_file: InterruptOnConfig = InterruptOnConfig(
    when=lambda req: req.tool_call["name"] == "write_file",
    allowed_decisions=["approve", "reject", "edit"],
)
interrupt_on_config_execute_sql: InterruptOnConfig = InterruptOnConfig(
    when=is_execute_sql,
    allowed_decisions=["approve", "reject"],
)
INTERRUPT_ON = {
    "write_file": interrupt_on_config_write_file,
    "execute_sql": interrupt_on_config_execute_sql,
}
TOOLS = {item.name: item for item in [write_file, execute_sql, read_data]}


def build_agent(interrupt_mode: Literal["batched", "per_call"], model="ollama:llama3.1"):
    return create_agent(
        model=model,
        tools=list(TOOLS.values()),
        middleware=[
            HumanInTheLoopMiddleware(
                interrupt_on=INTERRUPT_ON,
                # batched：每轮模型调用后统一审批；per_call：每次工具调用分别审批。
                interrupt_mode=interrupt_mode,
                description_prefix="Tool execution pending approval",
            )
        ],
        checkpointer=InMemorySaver(),
    )


def ask_decision(action: dict, allowed_decisions: list[str]) -> dict:
    print("Approval request:", action.get("description", ""))
    print("\tname:", action["name"])
    print("\targs:", action["args"])
    choices = {"y": "approve", "n": "reject", "e": "edit"}
    choices = {key: value for key, value in choices.items() if value in allowed_decisions}
    prompt = ", ".join(f"{key}={value}" for key, value in choices.items())

    while True:
        try:
            choice = input(f"Enter your choice ({prompt}): ").strip().lower()
            decision_type = choices.get(choice)
            if decision_type is None:
                print("请输入当前工具允许的选项。")
                continue
            if decision_type == "approve":
                return {"type": "approve"}
            if decision_type == "reject":
                return {"type": "reject", "message": "User rejected execution."}

            # 编辑完整参数对象，而非给所有工具强塞 content 参数。
            print('请输入新的 JSON 参数，例如 {"content": "SELECT * FROM users;"}')
            args = json.loads(input("New args: "))
            if not isinstance(args, dict):
                print("工具参数必须是 JSON 对象。")
                continue
            TOOLS[action["name"]].tool_call_schema.model_validate(args)
            return {
                "type": "edit",
                "edited_action": {"name": action["name"], "args": args},
            }
        except (json.JSONDecodeError, ValidationError) as error:
            print(f"参数无效，请重新选择并输入：{error}")
        except EOFError:
            # 无交互输入时拒绝执行，避免意外批准工具调用。
            return {"type": "reject", "message": "No interactive input; execution rejected."}


def collect_decisions(interrupts) -> dict:
    resume_values = {}
    for item in interrupts:
        payload = item.value
        if payload.get("type") == "tool_approval":
            # per_call：中断 ID -> 单个 Decision，不能再包一层 decisions。
            allowed = INTERRUPT_ON[payload["name"]]["allowed_decisions"]
            resume_values[item.id] = ask_decision(payload, allowed)
        else:
            # batched：中断 ID -> {decisions: [...] }，按动作顺序逐一提交。
            action_decisions = []
            for action, review in zip(
                    payload["action_requests"], payload["review_configs"], strict=True
            ):
                action_decisions.append(ask_decision(action, review["allowed_decisions"]))
            resume_values[item.id] = {"decisions": action_decisions}
    return resume_values


def run_agent(agent):
    config = {"configurable": {"thread_id": "1501"}}
    response = agent.invoke(
        {
            "messages": [
                SystemMessage(
                    "You are a helpful assistant. Important: when you need to write file "
                    "or execute sql or read data, you must use the tools provided."
                ),
                HumanMessage("Delete all user from the database and write sql to file."),
            ]
        },
        config=config,
        version="v2"
    )
    # 后续模型轮次也可能请求审批，持续处理直到没有中断。
    while response.get("__interrupt__"):
        resume_values = collect_decisions(response["__interrupt__"])
        response = agent.invoke(Command(resume=resume_values), config=config)
    return response


def main():
    parser = argparse.ArgumentParser(description="Human-in-the-loop 工具审批示例")
    parser.add_argument("--interrupt-mode", choices=["batched", "per_call"], default="batched")
    args = parser.parse_args()
    load_dotenv()
    agent = build_agent(args.interrupt_mode)
    response = run_agent(agent)
    for message in response["messages"]:
        message.pretty_print()


if __name__ == "__main__":
    main()
