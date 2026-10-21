from typing import TypedDict

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import (
    HumanInTheLoopMiddleware,
    ModelRetryMiddleware,
    ToolErrorMiddleware,
)
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import ToolRuntime
from langgraph.prebuilt.tool_node import ToolCallRequest
from langgraph.types import Command
from pydantic import BaseModel

load_dotenv()


class CustomState(TypedDict):
    my_email: str


class Email(BaseModel):
    subject: str
    body: str
    recipient: str


class InvalidEmailException(Exception):
    def __init__(self, email_id: str):
        self.message = f"无效的邮件地址: #{email_id}" if email_id else "无效的邮件地址"
        super().__init__(self.message)


@tool
def read_email(email_id: str) -> dict | None:
    """Read an email from the mailbox"""
    return {
        "subject": "周五聚会安排",
        "content": "你好，周五安排在海边聚餐！有空参加活动吗？期待你的回复！",
        "from_email": "阿斯科利<ath@happ.com>",
        "date": "2026-10-20 22:00:00"
    } if email_id == "1234" else None


@tool
def send_email(email: Email, runtime: ToolRuntime) -> str:
    """Send an email with subject, body, and recipient address."""
    sender_address = runtime.state.get("my_email")
    if not sender_address:
        raise InvalidEmailException("")
    print(f"给 {email.recipient} 发送邮件")
    return f"给 {email.recipient} 的邮件发送成功!"


def on_error(exception: Exception, request: ToolCallRequest) -> str | None:
    if isinstance(exception, InvalidEmailException):
        return f"{request.tool_call['name']} 调用出错: {type(exception).__name__}"
    return None


tool_error_middleware = ToolErrorMiddleware(
    on_error=on_error,
)

retry_middleware = ModelRetryMiddleware(
    max_retries=2,
    backoff_factor=2.0,
    initial_delay=1
)

human_in_the_loop_middleware = HumanInTheLoopMiddleware(
    interrupt_on={
        "send_email": {
            "allowed_decisions": ["approve", "edit", "reject"]
        },
        "read_email": False
    }
)

agent = create_agent(
    model="ollama:gemma4:12b",
    tools=[read_email, send_email],
    state_schema=CustomState,
    middleware=[tool_error_middleware, retry_middleware, human_in_the_loop_middleware],
    checkpointer=InMemorySaver()
)
messages = [HumanMessage("帮我回复邮件1234，我可以参加活动。")]
config: RunnableConfig = {"configurable": {"thread_id": "email-reply-1234"}}
response = agent.invoke(
    {
        "messages": messages,
        "my_email": "ab@happ.com"
    },
    config=config
)

if response.get("__interrupt__"):
    paused = response["__interrupt__"][0]
    for action in paused.value["action_requests"]:
        print("待发送邮件")
        print(action)

    try:
        choice = input("是否发送邮件？输入 y 发送，输入 e 编辑，输入 c 取消。").strip().lower()
    except EOFError:
        # No interactive input: reject the pending side effect safely.
        print("没有可用的交互式输入，已取消发送。")
        choice = "c"

    if choice == "y":
        decision = {"type": "approve"}
    elif choice == "c":
        decision = {"type": "reject"}
    else:
        decision = {
            "type": "edit",
            "edited_action": {
                "name": "send_email",
                "args": {
                    "email": {
                        "subject": "聚会安排回复",
                        "body": "我可以准时参加！",
                        "recipient": "ath@happ.com",
                    }
                }
            }
        }

    response = agent.invoke(
        Command(resume={"decisions": [decision]}),
        config=config
    )

for msg in response["messages"]:
    msg.pretty_print()
