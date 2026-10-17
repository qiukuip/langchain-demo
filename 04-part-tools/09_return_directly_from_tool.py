from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.tools import tool

load_dotenv()


@tool(return_direct=True)
def fetch_order_status(order_id: str) -> str:
    """Fetch the current status of a customer order."""
    return f"Order #{order_id} is shipped and will arrive in 2 days."


agent = create_agent(
    model="google_genai:gemini-3.1-flash-lite",
    tools=[fetch_order_status]
)
result = agent.invoke({"messages": [{"role": "user", "content": "What is the status of order #12345?"}]})
print(result)
print("=====\n")
print(result["messages"][-1].content_blocks)
