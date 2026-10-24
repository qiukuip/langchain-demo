import asyncio

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.mcp import MCPAdapter
from langchain.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

load_dotenv()


async def answer_question(question: dict) -> dict:
    """Collect the email and age requested by the profile tool."""
    print(f"\n服务端请求：{question['message']}")
    if question["mode"] != "form":
        print("本示例只处理资料表单，已取消请求。")
        return {"action": "cancel"}
    print(f"表单结构：{question['requested_schema']}")
    try:
        choice = (await asyncio.to_thread(
            input, "输入 y 提供资料，n 拒绝提供，其他输入取消创建："
        )).strip().lower()
        if choice == "n":
            return {"action": "decline"}
        if choice != "y":
            return {"action": "cancel"}
        email = (await asyncio.to_thread(input, "邮箱：")).strip()
        age = int(await asyncio.to_thread(input, "年龄："))
    except (EOFError, ValueError):
        print("没有有效输入，已取消创建。")
        return {"action": "cancel"}
    return {"action": "accept", "content": {"email": email, "age": age}}


async def main():
    async with MCPAdapter("http://localhost:8000/mcp") as client:
        tools = await client.list_tools()
        for tool in tools:
            print(f"Found tool: {tool.name} => {tool.description}")

        agent = create_agent(
            model="ollama:llama3.1",
            tools=tools,
            system_prompt=(
                "Use create_profile to create the user's profile. "
                "The tool requests missing details itself. "
                "Respect declined or cancelled requests and do not retry them."
            ),
            checkpointer=InMemorySaver()
        )
        config: RunnableConfig = {
            "configurable": {
                "thread_id": "1406"
            }
        }
        response = await agent.ainvoke(
            {
                "messages": [HumanMessage("Create a profile for me, my name is Alice.")]
            },
            config=config,
        )

        # 可能没有中断，也可能有多个工具或多轮问题，不能直接解包单个中断。
        while response.get("__interrupt__"):
            answers_by_interrupt = {}
            for interruption in response["__interrupt__"]:
                payload = interruption.value
                if payload.get("type") != "mcp_elicitation":
                    raise ValueError(f"Unexpected interrupt: {payload}")
                answers = {}
                for question in payload["requests"]:
                    answers[question["key"]] = await answer_question(question)
                answers_by_interrupt[interruption.id] = {"responses": answers}

            # 使用同一个 thread_id，在 MCPAdapter 连接仍打开时恢复。
            response = await agent.ainvoke(
                Command(resume=answers_by_interrupt), config=config
            )

        for message in response["messages"]:
            message.pretty_print()


if __name__ == "__main__":
    asyncio.run(main())
