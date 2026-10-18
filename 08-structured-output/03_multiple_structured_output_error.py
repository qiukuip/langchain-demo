from typing import Union

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.structured_output import (
    MultipleStructuredOutputsError,
    StructuredOutputValidationError,
    ToolStrategy,
)
from pydantic import BaseModel, Field

load_dotenv()


class ContactInfo(BaseModel):
    """主持人信息"""

    name: str = Field(description="Person's name")
    email: str = Field(description="Email address")


class EventDetails(BaseModel):
    """事件的信息"""

    event_name: str = Field(description="Name of the event")
    date: str = Field(description="Event date")


class ProductRating(BaseModel):
    rating: int = Field(description="评分区间，评分必须在 1 分至 5 分之间", ge=1, le=5)
    comment: str = Field(description="评价的内容")


def custom_error_handler(error: Exception) -> str:
    if isinstance(error, StructuredOutputValidationError):
        return "格式有错误，请重试。"
    elif isinstance(error, MultipleStructuredOutputsError):
        return "请选择第一个结构化响应。"
    else:
        return f"错误：{str(error)}"


agent = create_agent(
    # model="google_genai:gemini-3.1-flash-lite",
    model="ollama:llama3.1",
    response_format=ToolStrategy(
        # 错误处理默认开启
        schema=Union[ContactInfo, EventDetails],
        tool_message_content="结构化处理已完成",
        handle_errors=custom_error_handler,
        # 无错误处理
        # handle_errors=False
    ),
    # response_format=ToolStrategy(
    #     schema=ProductRating, handle_errors="请提供 1 - 5 之间的有效评分和对应的评价。"
    # ),
)
# system_message = SystemMessage("你是一个解析产品评分的助手，请不要编造任何字段和值。")
input_message = {
    "role": "user",
    "content": "帮我提取信息，纸巾大佬（zhijin@dalao.com）将于 2026 年 5 月 32 日主持召开年中财政会议。",
    # "content": "请解析以下同时包含评分和评价内容的评论：令人意外的产品，10/10！",
}
result = agent.invoke({"messages": [input_message]})
for msg in result["messages"]:
    if type(msg).__name__ == "ToolMessage":
        print(msg.content)
    elif isinstance(msg, dict) and msg.get("tool_call_id"):
        print(msg["content"])
