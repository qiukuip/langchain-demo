from dotenv import load_dotenv
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langgraph.prebuilt import ToolRuntime
from langgraph.types import Command

load_dotenv()


# 可以直接从工具退出并路由到图中的其他节点
@tool(return_direct=True)
def fetch_and_store_order(order_id: str, runtime: ToolRuntime) -> Command:
    """Fetch order status and store it in state."""
    status = f"Order #{order_id} is shipped and will arrive in 2 days."
    return Command(
        update={
            "last_order_status": status,
            "messages": [
                ToolMessage(
                    content=status,
                    tool_call_id=runtime.tool_call_id
                )
            ]
        },
        goto="parent_node_name",
        graph=Command.PARENT
    )
