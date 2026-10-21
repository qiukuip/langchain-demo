from typing import List

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import ToolErrorMiddleware
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.tools import tool
from langgraph.prebuilt.tool_node import ToolCallRequest

load_dotenv()


class ToolCallingFakeModel(GenericFakeChatModel):
    def bind_tools(self, tools, **kwargs):
        return self


@tool
def self_define_calculate(a: int, b: int) -> int:
    """两个整数自定义运算"""
    if a == 10 or b == 20:
        raise ValueError("10 或者 20 不能参与运算！")
    return a * b


def on_error(exception: Exception, request: ToolCallRequest) -> str | None:
    if isinstance(exception, ValueError):
        return f"{request.tool_call['name']} 由于 {type(exception).__name__} 错误调用失败."
    return None


messages: List[BaseMessage] = [
    HumanMessage(content="10 与 100 的自定义运算结果等于？"),
]

model = ToolCallingFakeModel(
    messages=iter(
        [
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "self_define_calculate",
                        "args": {"a": 10, "b": 100},
                        "id": "call_0902",
                    }
                ],
            ),
            AIMessage(content="工具失败已由中间件处理。"),
        ]
    )
)
agent = create_agent(
    model=model,
    tools=[self_define_calculate],
    middleware=[ToolErrorMiddleware(on_error=on_error)],
)
result = agent.invoke(
    {"messages": messages}
)
for msg in result["messages"]:
    print(msg.pretty_print())
