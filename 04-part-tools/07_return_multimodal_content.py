from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool
from langgraph.prebuilt import ToolRuntime


@tool
def capture_screenshot(runtime: ToolRuntime) -> list[dict]:
    """Capture a screenshot of the current page."""
    return [
        {"type": "text", "text": "Screenshot of current page"},
        {"type": "image", "url": "https://assets.699pic.com/public/img95/photo/50103/6193.jpg_wh860.jpg"}
    ]


load_dotenv()

agent = create_agent(
    model="google_genai:gemini-3.1-flash-lite",
    tools=[capture_screenshot],
    system_prompt=SystemMessage("You are a helpful assistant. When need to capture screen, you can use provided tool.")
)
messages = [HumanMessage("Capture screenshot")]
result = agent.invoke({
    "messages": messages,
})
print(result["messages"][-1].content_blocks)
