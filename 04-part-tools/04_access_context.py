from dataclasses import dataclass

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import ToolRuntime, tool
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

USER_DATA = {
    "user123": {
        "name": "Alice Johnson",
        "account_type": "Premium",
        "balance": 5000,
        "email": "alice@example.com",
    },
    "user456": {
        "name": "Bob Smith",
        "account_type": "Standard",
        "balance": 1200,
        "email": "bob@example.com",
    },
}


@dataclass
class UserContext:
    user_id: str


@tool
def get_account_info(runtime: ToolRuntime[UserContext]) -> str:
    """Get current user's account information."""
    user_id = runtime.context.user_id

    if user_id in USER_DATA:
        user = USER_DATA[user_id]
        return f"Account holder: {user['name']}\nAccount type: {user['account_type']}\nBalance: {user['balance']}\nEmail{user['email']}"
    return "User not found!"


model = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")
agent = create_agent(
    model=model,
    tools=[get_account_info],
    context_schema=UserContext,
    system_prompt="You are a financial assistant.",
)
result = agent.invoke(
    {"messages": [{"role": "user", "content": "What's my current balance"}]},
    context=UserContext("user456"),
)
print(result["messages"][-1].content_blocks)
