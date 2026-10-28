from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.tools import tool

load_dotenv()


@tool
def send_email(to: str, subject: str, body: str):
    """Send an email."""
    email = {
        "to": to,
        "subject": subject,
        "body": body
    }
    return f"Email sent to {to}."


agent = create_agent(
    model="ollama:llama3.1",
    tools=[send_email],
    system_prompt="You are an email assistant. Always use the send_email tool."
)
response = agent.invoke(
    {"messages": [{"role": "user", "content": "Send an email greet email to Alice."}]}
)
print(response["messages"][-1].content_blocks)
