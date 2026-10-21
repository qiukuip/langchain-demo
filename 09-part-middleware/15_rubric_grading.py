"""让 RubricMiddleware 按评分标准检查并迭代修改 Agent 回复。"""

from dotenv import load_dotenv
from deepagents import RubricMiddleware
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

load_dotenv()


def report_evaluation(evaluation: dict) -> None:
    """打印每轮评分结果；需要修改时，Middleware 会把反馈交给 Agent。"""
    print(f"\n第 {evaluation['iteration'] + 1} 轮评分：{evaluation['result']}")
    print(evaluation["explanation"])

    for criterion in evaluation["criteria"]:
        if criterion["passed"]:
            print(f"  ✓ {criterion['name']}")
        else:
            print(f"  ✗ {criterion['name']}：{criterion['gap']}")


model = "google_genai:gemini-3.6-flash"

agent = create_agent(
    model=model,
    tools=[],
    middleware=[
        RubricMiddleware(
            model=model,
            max_iterations=3,
        )
    ],
)

rubric = """
请按以下标准评估 Agent 的最终回复：
1. 回复是一则面向微信群的公园清洁活动招募通知。
2. 明确写出活动日期为 2026-11-07，集合地点为东门。
3. 包含清晰的报名行动号召。
每项标准都必须满足；未满足时给出具体、可执行的修改建议。
"""

print("开始生成回复；生成后 Rubric grader 会按标准评分。", flush=True)
printed_response_heading = False

for chunk in agent.stream(
    {
        "messages": [
            HumanMessage("帮我写一则简短的公园清洁活动招募通知，适合发到微信群。")
        ],
        "rubric": rubric,
    },
    stream_mode=["messages", "custom"],
    version="v2",
):
    if chunk["type"] == "messages":
        token, _metadata = chunk["data"]
        text = getattr(token, "text", "")
        if text:
            if not printed_response_heading:
                print("\nAgent 回复：", end="", flush=True)
                printed_response_heading = True
            print(text, end="", flush=True)
    elif chunk["type"] == "custom":
        event = chunk["data"]
        if event.get("type") == "rubric_evaluation_start":
            print(
                f"\n\n开始第 {event['iteration'] + 1} 轮评分...",
                flush=True,
            )
        elif event.get("type") == "rubric_evaluation_end":
            report_evaluation(event)

print("\n\n处理完成。")
