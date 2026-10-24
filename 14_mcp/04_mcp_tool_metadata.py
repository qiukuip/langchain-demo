import asyncio

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import InterruptOnConfig, HumanInTheLoopMiddleware
from langchain.mcp import MCPAdapter
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

load_dotenv()


def is_destructive(tool: BaseTool) -> bool:
    """Read the MCP destructive hint off the adapter's tool metadata."""
    annotations = (
        (tool.metadata or {}).get("mcp", {}).get("tool", {}).get("annotations", {})
    )
    return annotations.get("destructive_hint", False)


def review_action(action: dict) -> dict:
    """Ask for approval before executing a tool call."""
    print(f"\n待审核工具：{action['name']}")
    print(f"调用参数：{action['args']}")
    try:
        choice = input("是否批准执行？输入 y 批准，其他输入拒绝：").strip().lower()
    except EOFError:
        print("没有可用的交互式输入，已拒绝执行。")
        choice = "n"
    return {"type": "approve" if choice == "y" else "reject"}


async def main():
    async with MCPAdapter("http://localhost:8001/mcp") as adapter:
        tools = await adapter.list_tools()
        destructive_tools = []

        for tool in tools:
            print(f"Found tool: {tool.name} => {tool.description}")

            print(f"Tool metadata: {tool.metadata}")
            mcp_tool_metadata = (tool.metadata or {}).get("mcp", {}).get("tool", {})
            print(f"Custom metadata: {mcp_tool_metadata.get('_meta', {})}")
            annotations = mcp_tool_metadata.get("annotations", {})
            print(f"Destructive Hint: {annotations.get('destructive_hint', False)}")

            if is_destructive(tool):
                destructive_tools.append(tool.name)
        print("=====")

        gate = InterruptOnConfig(
            allowed_decisions=["approve", "reject"],
        )

        # destructive_tools 中保存的是工具名称字符串，而不是 BaseTool 对象。
        interrupt_on: dict[str, bool | InterruptOnConfig] = {
            tool_name: gate for tool_name in destructive_tools
        }
        print(f"需要人工审核的工具：{destructive_tools}")

        config: RunnableConfig = {
            "configurable": {
                "thread_id": "1404"
            }
        }
        agent = create_agent(
            model="ollama:llama3.1",
            system_prompt="Use the weather tool for weather queries. If a tool call is rejected, respect the decision and do not retry it.",
            tools=tools,
            middleware=[
                HumanInTheLoopMiddleware(interrupt_on=interrupt_on)
            ],
            checkpointer=InMemorySaver()
        )
        response = await agent.ainvoke(
            {"messages": [HumanMessage(content="What's the weather in San Francisco?")]},
            config=config
        )

        # 中断信息不在 messages 中；收集每个调用的决定后，用同一线程恢复。
        while response.get("__interrupt__"):
            decisions_by_interrupt = {}
            for interruption in response["__interrupt__"]:
                decisions = [
                    review_action(action)
                    for action in interruption.value["action_requests"]
                ]
                decisions_by_interrupt[interruption.id] = {"decisions": decisions}
            response = await agent.ainvoke(
                Command(resume=decisions_by_interrupt),
                config=config,
            )

        for message in response["messages"]:
            message.pretty_print()


if __name__ == "__main__":
    asyncio.run(main())
